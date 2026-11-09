from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.post import Post
from app.models.match import AgentMatch
from app.schemas import AgentMatchResponse
from app.services.relevance_service import relevance_service

router = APIRouter(prefix="/matching", tags=["Relevance Matching"])

def _build_match_response(m: AgentMatch) -> AgentMatchResponse:
    return AgentMatchResponse(
        id=m.id,
        post_id=m.post_id,
        matched_agent_id=m.matched_agent_id,
        matched_company_name=m.agent.company.name if m.agent and m.agent.company else "Unknown",
        matched_agent_name=m.agent.identity_name if m.agent else "Agent",
        matched_industry=m.agent.company.industry if m.agent and m.agent.company else "General",
        relevance_score=m.relevance_score,
        matching_reason=m.matching_reason,
        notification_status=m.notification_status,
        created_at=m.created_at
    )

@router.post("/{post_id}", response_model=List[AgentMatchResponse])
def trigger_matching(post_id: str, threshold: Optional[float] = Query(None), db: Session = Depends(get_db)):
    """Triggers the multi-factor relevance algorithm for a post and returns matched company agents."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    matches = relevance_service.run_relevance_matching_for_post(db, post_id, custom_threshold=threshold)
    return [_build_match_response(m) for m in matches]

@router.get("/{post_id}/results", response_model=List[AgentMatchResponse])
def get_matching_results(post_id: str, db: Session = Depends(get_db)):
    """Fetches all matched partner agents and relevance scores for a post."""
    matches = db.query(AgentMatch).filter(AgentMatch.post_id == post_id).order_by(AgentMatch.relevance_score.desc()).all()
    return [_build_match_response(m) for m in matches]
