import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=True)
    topic = Column(String(255), nullable=True, index=True)
    category = Column(String(100), nullable=True, index=True)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    matched_count = Column(Integer, default=0)
    is_simulated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    company = relationship("Company", back_populates="posts")
    agent = relationship("Agent", back_populates="posts")
    research_result = relationship("ResearchResult", back_populates="post", uselist=False)
    embeddings = relationship("PostEmbedding", back_populates="post", cascade="all, delete-orphan")
    matches = relationship("AgentMatch", back_populates="post", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    conversation = relationship("Conversation", back_populates="post", uselist=False, cascade="all, delete-orphan")
