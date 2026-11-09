import logging
from typing import Dict, Any, Optional, TypedDict, List
from sqlalchemy.orm import Session

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

from app.models.company import Company
from app.models.agent import Agent, AgentStatus
from app.models.post import Post
from app.models.comment import Comment
from app.models.conversation import Conversation
from app.models.notification import Notification, NotificationStatus
from app.services.gemini_service import gemini_service
from app.core.config import settings

logger = logging.getLogger(__name__)

class AgentWorkflowState(TypedDict):
    agent_id: str
    company_name: str
    industry: str
    system_instructions: str
    post_id: str
    post_title: str
    post_content: str
    post_author_co: str
    parent_comment_id: Optional[str]
    conversation_depth: int
    decision: str
    reasoning: str
    generated_response: Optional[str]
    published_comment_id: Optional[str]
    should_continue: bool
    is_simulated: bool

class LangGraphService:
    def __init__(self):
        self.max_depth = settings.MAX_CONVERSATION_DEPTH
        self.max_responses = settings.MAX_RESPONSES_PER_POST

    # Node 1: Relevance and Strategic Evaluation
    def assess_opportunity_node(self, state: AgentWorkflowState) -> AgentWorkflowState:
        agent_company = {
            "name": state["company_name"],
            "industry": state["industry"],
            "products_services": "",
            "business_objectives": ""
        }
        post_data = {
            "title": state["post_title"],
            "content": state["post_content"],
            "company_name": state["post_author_co"],
            "industry": ""
        }

        eval_result = gemini_service.evaluate_opportunity(
            agent_company=agent_company,
            system_instructions=state["system_instructions"],
            post_data=post_data
        )

        state["decision"] = eval_result.get("decision", "RESPOND")
        state["reasoning"] = f"{eval_result.get('relevance_assessment', '')} Opportunity: {eval_result.get('business_opportunity', '')}".strip()
        state["generated_response"] = eval_result.get("response_content")
        state["is_simulated"] = eval_result.get("is_simulated", False)
        
        if state["decision"] == "IGNORE":
            state["should_continue"] = False
        else:
            state["should_continue"] = True
            
        return state

    # Node 2: Safety, Guardrails & Anti-Loop Node
    def guardrails_node(self, state: AgentWorkflowState) -> AgentWorkflowState:
        # Check depth
        if state["conversation_depth"] >= self.max_depth:
            state["should_continue"] = False
            state["decision"] = "IGNORE"
            state["reasoning"] += f" [Guardrail: Max conversation depth of {self.max_depth} reached.]"
            return state

        return state

    # Node 3: Synthesize Contextual Comment
    def synthesize_response_node(self, state: AgentWorkflowState) -> AgentWorkflowState:
        if not state["should_continue"] or not state["generated_response"]:
            return state

        # If replying to a specific sub-thread, tailor tone
        if state["parent_comment_id"]:
            state["generated_response"] = f"In response to the proposal: {state['generated_response']}"
            
        return state

    def build_langgraph_graph(self):
        """Constructs LangGraph StateGraph instance if library is available."""
        if not LANGGRAPH_AVAILABLE:
            return None
        try:
            workflow = StateGraph(AgentWorkflowState)
            workflow.add_node("assess_opportunity", self.assess_opportunity_node)
            workflow.add_node("guardrails", self.guardrails_node)
            workflow.add_node("synthesize_response", self.synthesize_response_node)

            workflow.set_entry_point("assess_opportunity")
            workflow.add_edge("assess_opportunity", "guardrails")
            workflow.add_edge("guardrails", "synthesize_response")
            workflow.add_edge("synthesize_response", END)

            return workflow.compile()
        except Exception as e:
            logger.warning(f"Could not initialize LangGraph StateGraph: {e}")
            return None

    def execute_agent_response(
        self,
        db: Session,
        agent_id: str,
        post_id: str,
        notification_id: Optional[str] = None,
        parent_comment_id: Optional[str] = None,
        override_decision: Optional[str] = None
    ) -> Dict[str, Any]:
        """Executes the autonomous agent decision and posting pipeline."""
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            raise ValueError(f"Agent {agent_id} not found.")
        if agent.status != AgentStatus.ACTIVE:
            raise ValueError(f"Agent {agent.identity_name} is not ACTIVE (current status: {agent.status}).")

        # Check if agent is paused
        if agent.configuration and agent.configuration.is_paused:
            raise ValueError(f"Agent {agent.identity_name} is currently PAUSED.")

        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise ValueError(f"Post {post_id} not found.")

        # Duplicate response prevention: Check if this agent already commented on this post
        existing_comment = db.query(Comment).filter(
            Comment.post_id == post.id,
            Comment.agent_id == agent.id
        ).first()

        # Allow counter-reply if it's the post author or replying to another comment
        if existing_comment and not parent_comment_id and agent.company_id != post.company_id:
            logger.info(f"Agent {agent.identity_name} already commented on post {post_id}. Skipping to prevent duplicate.")
            return {
                "decision": "IGNORE",
                "reasoning": "Duplicate prevention: Agent already contributed to this post.",
                "comment": None,
                "is_duplicate": True
            }

        # Check or create conversation tracking
        conv = db.query(Conversation).filter(Conversation.post_id == post.id).first()
        current_depth = 0
        if not conv:
            conv = Conversation(
                post_id=post.id,
                participating_agent_ids=[post.agent_id],
                message_count=0,
                depth=0,
                status="ACTIVE"
            )
            db.add(conv)
            db.flush()
        else:
            current_depth = conv.depth
            if conv.status == "PAUSED" or conv.status == "CLOSED":
                return {
                    "decision": "IGNORE",
                    "reasoning": f"Conversation is currently {conv.status}.",
                    "comment": None
                }
            if conv.message_count >= self.max_responses:
                return {
                    "decision": "IGNORE",
                    "reasoning": f"Max responses limit ({self.max_responses}) reached for this conversation.",
                    "comment": None
                }

        initial_state: AgentWorkflowState = {
            "agent_id": agent.id,
            "company_name": agent.company.name,
            "industry": agent.company.industry,
            "system_instructions": agent.system_instructions,
            "post_id": post.id,
            "post_title": post.title,
            "post_content": post.content,
            "post_author_co": post.company.name,
            "parent_comment_id": parent_comment_id,
            "conversation_depth": current_depth,
            "decision": override_decision or "RESPOND",
            "reasoning": "",
            "generated_response": None,
            "published_comment_id": None,
            "should_continue": True,
            "is_simulated": False
        }

        # Run StateGraph if compiled, or step-through nodes
        compiled_graph = self.build_langgraph_graph()
        if compiled_graph:
            try:
                final_state = compiled_graph.invoke(initial_state)
            except Exception as e:
                logger.warning(f"LangGraph execution exception: {e}. Running sequential fallback.")
                s1 = self.assess_opportunity_node(initial_state)
                s2 = self.guardrails_node(s1)
                final_state = self.synthesize_response_node(s2)
        else:
            s1 = self.assess_opportunity_node(initial_state)
            s2 = self.guardrails_node(s1)
            final_state = self.synthesize_response_node(s2)

        # Allow user override if provided
        if override_decision:
            final_state["decision"] = override_decision

        new_comment = None
        if final_state["decision"] in ["RESPOND", "REQUEST_INFO"] and final_state.get("generated_response"):
            new_comment = Comment(
                post_id=post.id,
                company_id=agent.company_id,
                agent_id=agent.id,
                parent_comment_id=parent_comment_id,
                content=final_state["generated_response"],
                decision=final_state["decision"],
                reasoning=final_state["reasoning"],
                is_simulated=final_state.get("is_simulated", False)
            )
            db.add(new_comment)
            db.flush()

            # Update conversation metadata
            conv.message_count += 1
            conv.depth = max(conv.depth, current_depth + 1)
            participants = list(conv.participating_agent_ids or [])
            if agent.id not in participants:
                participants.append(agent.id)
            conv.participating_agent_ids = participants

            # Update post comments counter
            post.comments_count += 1

            final_state["published_comment_id"] = new_comment.id

        # Update notification status if provided
        if notification_id:
            notif = db.query(Notification).filter(Notification.id == notification_id).first()
            if notif:
                notif.status = NotificationStatus.RESPONDED if new_comment else NotificationStatus.IGNORED

        db.commit()

        return {
            "decision": final_state["decision"],
            "reasoning": final_state["reasoning"],
            "comment_id": new_comment.id if new_comment else None,
            "comment_content": new_comment.content if new_comment else None,
            "is_simulated": final_state.get("is_simulated", False)
        }

langgraph_service = LangGraphService()
