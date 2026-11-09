from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.company import Company
from app.models.agent import Agent, AgentStatus
from app.models.research import ResearchResult
from app.models.post import Post
from app.models.notification import Notification
from app.models.conversation import Conversation
from app.models.match import AgentMatch
from app.models.comment import Comment
from app.schemas import MetricsResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/metrics", response_model=MetricsResponse)
def get_system_metrics(db: Session = Depends(get_db)):
    """Computes real-time platform KPIs for the SaaS dashboard."""
    total_companies = db.query(func.count(Company.id)).scalar() or 0
    total_agents = db.query(func.count(Agent.id)).scalar() or 0
    active_agents = db.query(func.count(Agent.id)).filter(Agent.status == AgentStatus.ACTIVE).scalar() or 0
    total_research = db.query(func.count(ResearchResult.id)).scalar() or 0
    total_posts = db.query(func.count(Post.id)).scalar() or 0
    total_notifications = db.query(func.count(Notification.id)).scalar() or 0
    total_conversations = db.query(func.count(Conversation.id)).scalar() or 0

    return MetricsResponse(
        total_companies=total_companies,
        total_agents=total_agents,
        active_agents=active_agents,
        total_research=total_research,
        total_posts=total_posts,
        total_notifications=total_notifications,
        total_conversations=total_conversations
    )

@router.get("/activity")
def get_recent_activity(limit: int = 15, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Aggregates a unified live event stream across posts, matches, and comments."""
    activity = []

    # Recent posts
    recent_posts = db.query(Post).order_by(Post.created_at.desc()).limit(5).all()
    for p in recent_posts:
        activity.append({
            "id": p.id,
            "type": "POST_PUBLISHED",
            "title": f"{p.company.name} published '{p.title[:50]}...'",
            "detail": p.content[:120] + "...",
            "timestamp": p.created_at.isoformat(),
            "actor": p.company.name,
            "badge": "Brand Post"
        })

    # Recent comments
    recent_comments = db.query(Comment).order_by(Comment.created_at.desc()).limit(5).all()
    for c in recent_comments:
        activity.append({
            "id": c.id,
            "type": "AGENT_COMMENT",
            "title": f"{c.company.name} Agent responded ({c.decision})",
            "detail": c.content[:120] + "...",
            "timestamp": c.created_at.isoformat(),
            "actor": c.agent.identity_name,
            "badge": "Agent Dialogue"
        })

    # Recent matches
    recent_matches = db.query(AgentMatch).order_by(AgentMatch.created_at.desc()).limit(5).all()
    for m in recent_matches:
        activity.append({
            "id": m.id,
            "type": "RELEVANCE_MATCH",
            "title": f"Synergy Match: {m.agent.company.name} (Score: {m.relevance_score:.2f})",
            "detail": m.matching_reason[:120] + "...",
            "timestamp": m.created_at.isoformat(),
            "actor": "Relevance Engine",
            "badge": "Match Alert"
        })

    # Sort descending by timestamp
    activity.sort(key=lambda x: x["timestamp"], reverse=True)
    return activity[:limit]
