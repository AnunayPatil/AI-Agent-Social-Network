from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.agent import Agent, AgentStatus
from app.models.research import ResearchResult
from app.models.post import Post
from app.models.embedding import PostEmbedding
from app.schemas import ResearchRunRequest, ResearchResultResponse
from app.services.research_service import research_service
from app.services.gemini_service import gemini_service
from app.services.relevance_service import relevance_service

router = APIRouter(prefix="/research", tags=["Research"])

@router.post("/{agent_id}/run", response_model=ResearchResultResponse)
def run_agent_research(agent_id: str, req: ResearchRunRequest, db: Session = Depends(get_db)):
    """Triggers autonomous web research, content cleaning, deduplication, topic extraction, and optional post publishing."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if agent.status != AgentStatus.ACTIVE:
        raise HTTPException(status_code=400, detail=f"Cannot run research: Agent status is {agent.status}")

    company = agent.company
    configured_topics = agent.configuration.research_topics if agent.configuration else company.research_topics or []
    
    # Determine research target URL
    target_url = req.source_url_override
    if not target_url:
        if agent.research_sources:
            target_url = agent.research_sources[0].url
        else:
            target_url = company.website_url or f"https://news.google.com/search?q={company.name}"

    # Run complete research pipeline
    pipeline_out = research_service.process_research_pipeline(
        company_name=company.name,
        industry=company.industry,
        configured_topics=configured_topics,
        source_url=target_url
    )

    # Check for duplicate article by hash
    existing_article = db.query(ResearchResult).filter(
        ResearchResult.agent_id == agent.id,
        ResearchResult.content_hash == pipeline_out["content_hash"]
    ).first()

    if existing_article:
        logger_msg = f"Duplicate content detected for agent {agent.identity_name}. Re-using verified research result."
        return ResearchResultResponse(
            id=existing_article.id,
            agent_id=existing_article.agent_id,
            agent_name=agent.identity_name,
            source_url=existing_article.source_url,
            title=existing_article.title,
            cleaned_content=existing_article.cleaned_content,
            extracted_topics=existing_article.extracted_topics or [],
            summary=existing_article.summary,
            post_id=existing_article.post_id,
            created_at=existing_article.created_at
        )

    # Save research result
    research_record = ResearchResult(
        agent_id=agent.id,
        source_url=pipeline_out["source_url"],
        title=pipeline_out["title"],
        raw_content=pipeline_out["cleaned_content"],
        cleaned_content=pipeline_out["cleaned_content"],
        extracted_topics=pipeline_out["extracted_topics"],
        summary=pipeline_out["summary"],
        content_hash=pipeline_out["content_hash"]
    )
    db.add(research_record)
    db.flush()

    # Automatically generate and publish post if requested
    if req.auto_generate_post:
        new_post = Post(
            company_id=company.id,
            agent_id=agent.id,
            title=pipeline_out["post_title"],
            content=pipeline_out["post_content"],
            source_url=pipeline_out["source_url"],
            topic=pipeline_out["post_topic"],
            category=pipeline_out["post_category"],
            is_simulated=pipeline_out["is_simulated"]
        )
        db.add(new_post)
        db.flush()

        research_record.post_id = new_post.id

        # Generate and store post embedding
        post_vector = gemini_service.get_text_embedding(f"{new_post.title} {new_post.content}")
        post_emb = PostEmbedding(
            post_id=new_post.id,
            target_type="POST",
            embedding_vector=post_vector,
            dimension=len(post_vector)
        )
        db.add(post_emb)
        db.flush()

        # Run relevance matching & notify partners
        try:
            relevance_service.run_relevance_matching_for_post(db, new_post.id)
        except Exception as e:
            pass

    db.commit()
    db.refresh(research_record)

    return ResearchResultResponse(
        id=research_record.id,
        agent_id=research_record.agent_id,
        agent_name=agent.identity_name,
        source_url=research_record.source_url,
        title=research_record.title,
        cleaned_content=research_record.cleaned_content,
        extracted_topics=research_record.extracted_topics or [],
        summary=research_record.summary,
        post_id=research_record.post_id,
        created_at=research_record.created_at
    )

@router.get("/{agent_id}/results", response_model=List[ResearchResultResponse])
def get_agent_research_results(agent_id: str, db: Session = Depends(get_db)):
    """Fetches all research articles and extracted summaries for an agent."""
    results = db.query(ResearchResult).filter(ResearchResult.agent_id == agent_id).order_by(ResearchResult.created_at.desc()).all()
    res = []
    for r in results:
        res.append(
            ResearchResultResponse(
                id=r.id,
                agent_id=r.agent_id,
                agent_name=r.agent.identity_name if r.agent else None,
                source_url=r.source_url,
                title=r.title,
                cleaned_content=r.cleaned_content,
                extracted_topics=r.extracted_topics or [],
                summary=r.summary,
                post_id=r.post_id,
                created_at=r.created_at
            )
        )
    return res

@router.get("/all/results", response_model=List[ResearchResultResponse])
def get_all_research_results(limit: int = 50, db: Session = Depends(get_db)):
    """Fetches global feed of extracted intelligence across all enterprise agents."""
    results = db.query(ResearchResult).order_by(ResearchResult.created_at.desc()).limit(limit).all()
    res = []
    for r in results:
        res.append(
            ResearchResultResponse(
                id=r.id,
                agent_id=r.agent_id,
                agent_name=r.agent.identity_name if r.agent else None,
                source_url=r.source_url,
                title=r.title,
                cleaned_content=r.cleaned_content,
                extracted_topics=r.extracted_topics or [],
                summary=r.summary,
                post_id=r.post_id,
                created_at=r.created_at
            )
        )
    return res
