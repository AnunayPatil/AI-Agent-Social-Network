from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.post import Post
from app.models.company import Company
from app.models.agent import Agent
from app.models.embedding import PostEmbedding
from app.schemas import PostCreate, PostResponse
from app.services.gemini_service import gemini_service
from app.services.relevance_service import relevance_service

router = APIRouter(prefix="/posts", tags=["Posts"])

def _build_post_response(post: Post) -> PostResponse:
    return PostResponse(
        id=post.id,
        company_id=post.company_id,
        company_name=post.company.name if post.company else "Unknown",
        company_avatar=post.company.avatar_url if post.company else None,
        industry=post.company.industry if post.company else "General",
        agent_id=post.agent_id,
        agent_name=post.agent.identity_name if post.agent else "Autonomous Agent",
        title=post.title,
        content=post.content,
        source_url=post.source_url,
        topic=post.topic,
        category=post.category,
        likes_count=post.likes_count,
        comments_count=post.comments_count,
        matched_count=post.matched_count,
        is_simulated=post.is_simulated,
        created_at=post.created_at
    )

@router.post("", response_model=PostResponse, status_code=201)
def create_post(post_in: PostCreate, db: Session = Depends(get_db)):
    """Publishes a new brand post, computes semantic embedding, and triggers partner relevance matching."""
    company = db.query(Company).filter(Company.id == post_in.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    agent = db.query(Agent).filter(Agent.id == post_in.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    new_post = Post(
        company_id=company.id,
        agent_id=agent.id,
        title=post_in.title,
        content=post_in.content,
        source_url=post_in.source_url,
        topic=post_in.topic or company.industry,
        category=post_in.category or "Strategic Announcement",
        is_simulated=post_in.is_simulated
    )
    db.add(new_post)
    db.flush()

    # Generate and store embedding
    full_text = f"{new_post.title} {new_post.content} {new_post.topic or ''}"
    vector = gemini_service.get_text_embedding(full_text)
    post_emb = PostEmbedding(
        post_id=new_post.id,
        target_type="POST",
        embedding_vector=vector,
        dimension=len(vector)
    )
    db.add(post_emb)
    db.flush()

    # Trigger relevance matching if enabled
    if post_in.auto_trigger_matching:
        relevance_service.run_relevance_matching_for_post(db, new_post.id)

    db.commit()
    db.refresh(new_post)
    return _build_post_response(new_post)

@router.get("", response_model=List[PostResponse])
def get_social_feed(
    industry: Optional[str] = Query(None, description="Filter by company industry"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Returns Twitter/X-style feed with filtering and counters."""
    query = db.query(Post).join(Company, Post.company_id == Company.id)
    if industry and industry.lower() != "all":
        query = query.filter(Company.industry.ilike(f"%{industry}%"))
    
    posts = query.order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    return [_build_post_response(p) for p in posts]

@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: str, db: Session = Depends(get_db)):
    """Retrieves single post by ID."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return _build_post_response(post)

@router.post("/{post_id}/like", response_model=PostResponse)
def like_post(post_id: str, db: Session = Depends(get_db)):
    """Increments like count for a post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.likes_count += 1
    db.commit()
    db.refresh(post)
    return _build_post_response(post)
