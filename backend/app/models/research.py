import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class ResearchSource(Base):
    __tablename__ = "research_sources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type = Column(String(50), default="RSS")  # RSS, URL, API, COMPANY_WEBSITE
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="research_sources")

class ResearchResult(Base):
    __tablename__ = "research_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    source_url = Column(String(500), nullable=False)
    title = Column(String(500), nullable=False)
    raw_content = Column(Text, nullable=True)
    cleaned_content = Column(Text, nullable=False)
    extracted_topics = Column(JSON, default=list)
    summary = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=True, index=True)
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="research_results")
    post = relationship("Post", back_populates="research_result", uselist=False)
