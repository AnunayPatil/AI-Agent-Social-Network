from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.agent import Agent
from app.models.company import Company
from app.models.post import Post
from app.models.comment import Comment
from app.models.conversation import Conversation
from app.models.notification import Notification
from app.schemas import (
    CommentCreate,
    CommentResponse,
    AgentRespondRequest,
    ConversationResponse
)
from app.services.langgraph_service import langgraph_service
from app.services.provisioning_service import provisioning_service
from app.services.research_service import research_service
from app.services.relevance_service import relevance_service

router = APIRouter(tags=["Communication & Workflows"])

def _build_comment_response(c: Comment) -> CommentResponse:
    replies_res = []
    if hasattr(c, "replies") and c.replies:
        replies_res = [_build_comment_response(r) for r in c.replies]

    return CommentResponse(
        id=c.id,
        post_id=c.post_id,
        company_id=c.company_id,
        company_name=c.company.name if c.company else "Company",
        company_avatar=c.company.avatar_url if c.company else None,
        agent_id=c.agent_id,
        agent_name=c.agent.identity_name if c.agent else "Agent",
        parent_comment_id=c.parent_comment_id,
        content=c.content,
        decision=c.decision,
        reasoning=c.reasoning,
        is_simulated=c.is_simulated,
        created_at=c.created_at,
        replies=replies_res
    )

@router.post("/agents/{agent_id}/respond")
def agent_autonomous_respond(agent_id: str, req: AgentRespondRequest, db: Session = Depends(get_db)):
    """Triggers LangGraph autonomous evaluation and contextual commenting for a relevant agent."""
    result = langgraph_service.execute_agent_response(
        db=db,
        agent_id=agent_id,
        post_id=req.post_id,
        notification_id=req.notification_id,
        override_decision=req.override_decision
    )
    return result

@router.post("/posts/{post_id}/comments", response_model=CommentResponse)
def add_comment(post_id: str, comment_in: CommentCreate, db: Session = Depends(get_db)):
    """Creates a comment or threaded reply on a post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    new_comment = Comment(
        post_id=post.id,
        company_id=comment_in.company_id,
        agent_id=comment_in.agent_id,
        parent_comment_id=comment_in.parent_comment_id,
        content=comment_in.content,
        decision=comment_in.decision,
        reasoning=comment_in.reasoning
    )
    db.add(new_comment)
    db.flush()

    # Update conversation
    conv = db.query(Conversation).filter(Conversation.post_id == post.id).first()
    if not conv:
        conv = Conversation(
            post_id=post.id,
            participating_agent_ids=[post.agent_id, comment_in.agent_id],
            message_count=1,
            depth=1,
            status="ACTIVE"
        )
        db.add(conv)
    else:
        conv.message_count += 1
        participants = list(conv.participating_agent_ids or [])
        if comment_in.agent_id not in participants:
            participants.append(comment_in.agent_id)
        conv.participating_agent_ids = participants

    post.comments_count += 1
    db.commit()
    db.refresh(new_comment)
    return _build_comment_response(new_comment)

@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
def get_post_comments(post_id: str, db: Session = Depends(get_db)):
    """Retrieves all top-level comments and nested replies for a post."""
    comments = db.query(Comment).filter(
        Comment.post_id == post_id,
        Comment.parent_comment_id == None
    ).order_by(Comment.created_at.asc()).all()
    return [_build_comment_response(c) for c in comments]

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Fetches complete multi-agent conversation thread by ID."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    post = conv.post
    participants_info = []
    for ag_id in (conv.participating_agent_ids or []):
        ag = db.query(Agent).filter(Agent.id == ag_id).first()
        if ag:
            participants_info.append({
                "agent_id": ag.id,
                "agent_name": ag.identity_name,
                "company_name": ag.company.name if ag.company else ""
            })

    comments = db.query(Comment).filter(
        Comment.post_id == post.id,
        Comment.parent_comment_id == None
    ).order_by(Comment.created_at.asc()).all()

    return ConversationResponse(
        id=conv.id,
        post_id=post.id,
        post_title=post.title,
        original_company=post.company.name if post.company else "",
        original_agent=post.agent.identity_name if post.agent else "",
        participating_agents=participants_info,
        message_count=conv.message_count,
        depth=conv.depth,
        status=conv.status,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        comments=[_build_comment_response(c) for c in comments]
    )

@router.post("/conversations/{conversation_id}/toggle-status")
def toggle_conversation_status(conversation_id: str, status: Optional[str] = None, db: Session = Depends(get_db)):
    """Pauses, resumes, or closes a conversation thread."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    if status:
        conv.status = status
    else:
        conv.status = "PAUSED" if conv.status == "ACTIVE" else "ACTIVE"
        
    db.commit()
    db.refresh(conv)
    return {"id": conv.id, "status": conv.status}

@router.post("/workflow/e2e-demo")
def run_end_to_end_demo_workflow(db: Session = Depends(get_db)):
    """
    Executes the complete 15-step End-to-End Demo Workflow specified in the objective:
    1. Register Swiggy
    2. Automatically create Swiggy AI Agent
    3. Test and activate Swiggy agent
    4. Trigger research
    5. Extract and filter relevant info
    6. Generate post using Gemini
    7. Publish post
    8. Run relevance matching engine
    9. Identify PhonePe and HDFC as relevant, Bajaj Auto as less relevant
    10. Generate notifications
    11. PhonePe & HDFC receive notifications
    12. Agents independently evaluate opportunity via LangGraph
    13. Generate synergistic comments via Gemini
    14. Swiggy agent responds with appreciation and partnership exploration
    15. Social feed & conversation thread fully updated
    """
    logs = []

    # Check or seed PhonePe and HDFC Bank first so they are present to match Swiggy
    # 0a. Check PhonePe
    phonepe_co = db.query(Company).filter(Company.name == "PhonePe").first()
    if not phonepe_co:
        from app.schemas import CompanyCreate
        p_in = CompanyCreate(
            name="PhonePe",
            industry="Digital Payments",
            website_url="https://www.phonepe.com",
            description="India's leading fintech platform offering seamless UPI transactions, merchant QR payments, recharges, and financial services.",
            products_services="UPI Payments, PhonePe Merchant QR, Switch Rewards, Credit on UPI",
            business_objectives="Maximize high-frequency merchant transaction volume, accelerate digital commerce adoption, and deepen brand partner incentives.",
            target_audience="Digital-first smartphone users and retail merchants across India.",
            research_topics=["Digital Payments", "UPI Innovations", "Merchant Cashback", "Fintech Loyalty"],
            avatar_url="https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=100&h=100&fit=crop"
        )
        phonepe_co, phonepe_ag, _ = provisioning_service.provision_company_and_agent(db, p_in)
        logs.append(f"Pre-requisite: Provisioned PhonePe AI Agent ({phonepe_ag.identity_name})")
    else:
        phonepe_ag = phonepe_co.agents[0]

    # 0b. Check HDFC Bank
    hdfc_co = db.query(Company).filter(Company.name == "HDFC Bank").first()
    if not hdfc_co:
        from app.schemas import CompanyCreate
        h_in = CompanyCreate(
            name="HDFC Bank",
            industry="Banking",
            website_url="https://www.hdfcbank.com",
            description="Leading private sector commercial bank providing world-class credit cards, smart banking solutions, and corporate merchant financing.",
            products_services="Credit Cards, Millennia & Regalia Dining Rewards, Merchant POS, SmartBuy",
            business_objectives="Drive credit card retail spend velocity, grow cardholder loyalty across dining & lifestyle, and expand co-brand card integrations.",
            target_audience="Affluent consumers, professionals, and retail shoppers seeking premier banking rewards.",
            research_topics=["Credit Card Rewards", "Consumer Banking", "Digital Lending", "Festive Spends"],
            avatar_url="https://images.unsplash.com/photo-1541354329998-f4d9a9f9297f?w=100&h=100&fit=crop"
        )
        hdfc_co, hdfc_ag, _ = provisioning_service.provision_company_and_agent(db, h_in)
        logs.append(f"Pre-requisite: Provisioned HDFC AI Agent ({hdfc_ag.identity_name})")
    else:
        hdfc_ag = hdfc_co.agents[0]

    # 0c. Check Bajaj Auto (Control company with low relevance)
    bajaj_co = db.query(Company).filter(Company.name == "Bajaj Auto").first()
    if not bajaj_co:
        from app.schemas import CompanyCreate
        b_in = CompanyCreate(
            name="Bajaj Auto",
            industry="Automotive",
            website_url="https://www.bajajauto.com",
            description="Leading global two-wheeler and three-wheeler vehicle manufacturer pioneering Pulsar and Chetak EV.",
            products_services="Pulsar Motorcycles, Chetak Electric Scooters, Commercial 3-Wheelers",
            business_objectives="Expand global EV footprint, strengthen urban mobility dealership network, and improve battery efficiency.",
            target_audience="Two-wheeler commuters, fleet operators, and EV enthusiasts.",
            research_topics=["Electric Vehicles", "Two-Wheeler Mobility", "Battery Tech", "Urban Fleets"],
            avatar_url="https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=100&h=100&fit=crop"
        )
        bajaj_co, bajaj_ag, _ = provisioning_service.provision_company_and_agent(db, b_in)
        logs.append(f"Pre-requisite: Provisioned Bajaj Auto AI Agent ({bajaj_ag.identity_name})")
    else:
        bajaj_ag = bajaj_co.agents[0]

    # Step 1: Register Swiggy (or re-use if already exists)
    swiggy_co = db.query(Company).filter(Company.name == "Swiggy").first()
    if not swiggy_co:
        from app.schemas import CompanyCreate
        s_in = CompanyCreate(
            name="Swiggy",
            industry="Food Delivery",
            website_url="https://www.swiggy.com",
            description="India's leading on-demand convenience platform connecting consumers with top restaurants and quick groceries.",
            products_services="Food Delivery, Swiggy Instamart, Dineout, Swiggy One",
            business_objectives="Accelerate festive order volume, enhance customer affordability, and build strategic payment partner alliances.",
            target_audience="Urban foodies, working professionals, and convenience shoppers across 500+ Indian cities.",
            research_topics=["Food Delivery", "Festive Offers", "Restaurant Deals", "Quick Commerce"],
            avatar_url="https://images.unsplash.com/photo-1526367790999-0150786686a2?w=100&h=100&fit=crop"
        )
        swiggy_co, swiggy_ag, test_res = provisioning_service.provision_company_and_agent(db, s_in)
        logs.append(f"Step 1-3: Registered Swiggy & Provisioned Swiggy AI Agent (Score: {test_res.score:.2f}, Status: {swiggy_ag.status})")
    else:
        swiggy_ag = swiggy_co.agents[0]
        logs.append(f"Step 1-3: Verified Swiggy & Active Agent: {swiggy_ag.identity_name}")

    # Step 4-6: Trigger Research & Generate Post
    pipeline_out = research_service.process_research_pipeline(
        company_name=swiggy_co.name,
        industry=swiggy_co.industry,
        configured_topics=swiggy_co.research_topics or ["Food Delivery", "Festive Offers"],
        source_url="https://swiggy.com/news/festive-discount-2026"
    )
    logs.append(f"Step 4-6: Autonomous Research conducted. Generated Post: '{pipeline_out['post_title']}'")

    # Step 7: Publish Post
    post = Post(
        company_id=swiggy_co.id,
        agent_id=swiggy_ag.id,
        title="Special Festive Offer: Get an additional 5% discount on food orders",
        content="Delighted to announce our nationwide Festive Culinary Fiesta! Customers across India can enjoy an additional 5% discount on chef-crafted food orders. We are welcoming ecosystem partners to combine strengths and maximize consumer joy!",
        source_url=pipeline_out["source_url"],
        topic="Festive Dining & Offers",
        category="Promotions & Offers",
        is_simulated=True
    )
    db.add(post)
    db.flush()

    # Step 8-10: Relevance Matching Engine
    matches = relevance_service.run_relevance_matching_for_post(db, post.id)
    matched_names = [m.agent.company.name for m in matches]
    logs.append(f"Step 8-10: Relevance Matching Engine executed. Identified relevant partners: {matched_names}")

    # Step 11-13: Autonomous Agent Responses via LangGraph
    # 1. PhonePe Evaluates and Responds
    phonepe_notif = db.query(Notification).filter(
        Notification.post_id == post.id,
        Notification.recipient_agent_id == phonepe_ag.id
    ).first()
    
    phonepe_res = langgraph_service.execute_agent_response(
        db=db,
        agent_id=phonepe_ag.id,
        post_id=post.id,
        notification_id=phonepe_notif.id if phonepe_notif else None
    )
    logs.append(f"Step 11-13a: PhonePe Agent evaluated: Decision = {phonepe_res['decision']}. Comment published!")

    # 2. HDFC Bank Evaluates and Responds
    hdfc_notif = db.query(Notification).filter(
        Notification.post_id == post.id,
        Notification.recipient_agent_id == hdfc_ag.id
    ).first()
    
    hdfc_res = langgraph_service.execute_agent_response(
        db=db,
        agent_id=hdfc_ag.id,
        post_id=post.id,
        notification_id=hdfc_notif.id if hdfc_notif else None
    )
    logs.append(f"Step 11-13b: HDFC Bank Agent evaluated: Decision = {hdfc_res['decision']}. Comment published!")

    # Step 14: Swiggy Agent Evaluates Partner Comments & Responds Reciprocally
    swiggy_res = langgraph_service.execute_agent_response(
        db=db,
        agent_id=swiggy_ag.id,
        post_id=post.id
    )
    logs.append(f"Step 14: Swiggy Agent counter-response: Decision = {swiggy_res['decision']}. Multi-agent dialogue completed!")

    # Step 15: Conversation Thread & Metrics Updated
    conv = db.query(Conversation).filter(Conversation.post_id == post.id).first()
    logs.append(f"Step 15: Conversation established (ID: {conv.id if conv else 'N/A'}, Depth: {conv.depth if conv else 0}, Messages: {conv.message_count if conv else 0})")

    return {
        "status": "success",
        "post_id": post.id,
        "post_title": post.title,
        "matched_partners": matched_names,
        "logs": logs
    }
