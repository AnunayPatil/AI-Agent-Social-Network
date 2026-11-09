import logging
import math
from typing import Dict, Any, List, Optional
import numpy as np
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.agent import Agent, AgentStatus
from app.models.post import Post
from app.models.embedding import PostEmbedding
from app.models.match import AgentMatch
from app.models.notification import Notification, NotificationStatus
from app.services.gemini_service import gemini_service
from app.core.config import settings

logger = logging.getLogger(__name__)

class RelevanceService:
    def __init__(self):
        # Cross-industry synergy baseline weights
        self.industry_synergies = {
            ("food delivery", "digital payments"): 0.88,
            ("food delivery", "banking"): 0.82,
            ("food delivery", "fintech"): 0.85,
            ("food delivery", "automotive"): 0.20,
            ("food delivery", "mobility"): 0.35,
            
            ("digital payments", "banking"): 0.92,
            ("digital payments", "fintech"): 0.95,
            ("digital payments", "e-commerce"): 0.90,
            ("digital payments", "retail"): 0.85,
            ("digital payments", "automotive"): 0.30,
            
            ("banking", "automotive"): 0.75, # auto loans, fleet financing
            ("banking", "e-commerce"): 0.85,
            ("automotive", "mobility"): 0.90,
        }

    def compute_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Computes cosine similarity between two float vectors."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        v1 = np.array(vec1, dtype=np.float32)
        v2 = np.array(vec2, dtype=np.float32)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        dot = float(np.dot(v1, v2))
        sim = dot / (norm1 * norm2)
        return max(0.0, min(1.0, (sim + 1.0) / 2.0))  # normalize from [-1, 1] to [0, 1]

    def get_industry_synergy(self, ind1: str, ind2: str) -> float:
        """Looks up or estimates bidirectional industry synergy."""
        i1 = ind1.lower().strip()
        i2 = ind2.lower().strip()
        if i1 == i2:
            return 0.60  # Competitors / peers: moderate synergy for joint standards, but lower than cross-sell partners
        
        pair = (i1, i2)
        rev_pair = (i2, i1)
        if pair in self.industry_synergies:
            return self.industry_synergies[pair]
        if rev_pair in self.industry_synergies:
            return self.industry_synergies[rev_pair]
        
        # Partial match heuristics
        for (k1, k2), score in self.industry_synergies.items():
            if (k1 in i1 or i1 in k1) and (k2 in i2 or i2 in k2):
                return score
            if (k1 in i2 or i2 in k1) and (k2 in i1 or i1 in k2):
                return score
                
        return 0.35  # default moderate baseline

    def compute_keyword_overlap(self, post_text: str, agent_topics: List[str], products_services: str) -> float:
        """Calculates token overlap between post content and agent business domain."""
        post_tokens = set(post_text.lower().split())
        target_tokens = set()
        for t in agent_topics:
            target_tokens.update(t.lower().split())
        target_tokens.update(products_services.lower().split())
        
        # Remove common stopwords
        stopwords = {"the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "with", "is", "of", "our", "we", "this"}
        target_tokens = target_tokens - stopwords
        post_tokens = post_tokens - stopwords
        
        if not target_tokens or not post_tokens:
            return 0.0
            
        intersection = post_tokens.intersection(target_tokens)
        score = len(intersection) / min(15, len(target_tokens))
        return min(1.0, score)

    def evaluate_post_against_agent(self, post: Post, post_embedding_vec: List[float], agent: Agent, company: Company) -> Dict[str, Any]:
        """Calculates multi-factor relevance between a post and an candidate company agent."""
        # 1. Semantic Embedding Similarity
        # Agent vector: generated from company description + products + objectives
        agent_context = f"{company.name} in {company.industry}. {company.description}. Products: {company.products_services}. Objectives: {company.business_objectives}."
        agent_embedding_vec = gemini_service.get_text_embedding(agent_context)
        s_semantic = self.compute_cosine_similarity(post_embedding_vec, agent_embedding_vec)

        # 2. Industry Synergy
        s_industry = self.get_industry_synergy(post.company.industry, company.industry)

        # 3. Keyword Overlap
        topics = company.research_topics if isinstance(company.research_topics, list) else []
        post_full_text = f"{post.title} {post.content} {post.topic or ''} {post.category or ''}"
        s_keyword = self.compute_keyword_overlap(post_full_text, topics, company.products_services)

        # 4. Business Objectives Synergy
        obj_text = company.business_objectives.lower()
        s_objective = 0.50
        if any(term in post_full_text.lower() for term in ["offer", "discount", "transaction", "payment", "volume", "card", "partnership"]):
            if any(term in obj_text for term in ["checkout", "transaction", "cashback", "partner", "growth", "merchant", "alliance"]):
                s_objective = 0.88

        # Weighted aggregate score
        total_score = (0.40 * s_semantic) + (0.25 * s_industry) + (0.20 * s_keyword) + (0.15 * s_objective)
        total_score = round(float(total_score), 3)

        # Construct transparent matching reasoning
        reason = (
            f"Semantic similarity: {s_semantic:.2f} | Industry synergy ({post.company.industry} ↔ {company.industry}): {s_industry:.2f} | "
            f"Keyword overlap: {s_keyword:.2f} | Objective synergy: {s_objective:.2f}"
        )

        return {
            "agent_id": agent.id,
            "company_name": company.name,
            "agent_name": agent.identity_name,
            "industry": company.industry,
            "score": total_score,
            "s_semantic": s_semantic,
            "s_industry": s_industry,
            "s_keyword": s_keyword,
            "reason": reason
        }

    def run_relevance_matching_for_post(self, db: Session, post_id: str, custom_threshold: Optional[float] = None) -> List[AgentMatch]:
        """Runs the complete relevance matching engine for a newly published post."""
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise ValueError(f"Post with ID {post_id} not found.")

        # Ensure post has an embedding
        post_emb = db.query(PostEmbedding).filter(PostEmbedding.post_id == post.id).first()
        if not post_emb:
            vector = gemini_service.get_text_embedding(f"{post.title} {post.content}")
            post_emb = PostEmbedding(
                post_id=post.id,
                target_type="POST",
                embedding_vector=vector,
                dimension=len(vector)
            )
            db.add(post_emb)
            db.commit()
            db.refresh(post_emb)

        post_vector = post_emb.embedding_vector

        # Query all active agents excluding the post author's company
        candidate_agents = (
            db.query(Agent)
            .join(Company, Agent.company_id == Company.id)
            .filter(
                Agent.status == AgentStatus.ACTIVE,
                Agent.company_id != post.company_id  # Prevent matching own post!
            )
            .all()
        )

        matches_created = []
        threshold = custom_threshold if custom_threshold is not None else settings.DEFAULT_RELEVANCE_THRESHOLD

        for agent in candidate_agents:
            eval_result = self.evaluate_post_against_agent(
                post=post,
                post_embedding_vec=post_vector,
                agent=agent,
                company=agent.company
            )

            if eval_result["score"] >= threshold:
                # Check if match already exists
                existing = db.query(AgentMatch).filter(
                    AgentMatch.post_id == post.id,
                    AgentMatch.matched_agent_id == agent.id
                ).first()

                if not existing:
                    match_record = AgentMatch(
                        post_id=post.id,
                        matched_agent_id=agent.id,
                        relevance_score=eval_result["score"],
                        matching_reason=eval_result["reason"],
                        notification_status="PENDING"
                    )
                    db.add(match_record)
                    db.flush()
                    
                    # Create notification immediately if auto-notify is enabled
                    if settings.AUTO_NOTIFY_AGENTS:
                        notif = Notification(
                            recipient_agent_id=agent.id,
                            post_id=post.id,
                            match_id=match_record.id,
                            title=f"Synergy Alert: {post.company.name} posted '{post.title[:60]}...'",
                            message=f"Relevance Score: {eval_result['score']:.2f}. Matching factors: {eval_result['reason']}",
                            status=NotificationStatus.DELIVERED
                        )
                        db.add(notif)
                        match_record.notification_status = "DELIVERED"

                    matches_created.append(match_record)

        # Update post matched count
        post.matched_count = len(matches_created)
        db.commit()

        return matches_created

relevance_service = RelevanceService()
