import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), unique=True, nullable=False, index=True)
    industry = Column(String(100), nullable=False, index=True)
    website_url = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    products_services = Column(Text, nullable=False)
    business_objectives = Column(Text, nullable=False)
    target_audience = Column(Text, nullable=False)
    research_topics = Column(JSON, default=list)  # list of strings
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    agents = relationship("Agent", back_populates="company", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="company", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="company", cascade="all, delete-orphan")
