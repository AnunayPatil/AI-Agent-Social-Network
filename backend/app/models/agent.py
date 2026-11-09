import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base

class AgentStatus(str, Enum):
    PENDING = "Pending"
    TESTING = "Testing"
    ACTIVE = "Active"
    FAILED = "Failed"
    DISABLED = "Disabled"

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    identity_name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False, default="Autonomous Corporate Brand & Strategic Intelligence Agent")
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.PENDING, nullable=False, index=True)
    system_instructions = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="agents")
    configuration = relationship("AgentConfiguration", back_populates="agent", uselist=False, cascade="all, delete-orphan")
    research_sources = relationship("ResearchSource", back_populates="agent", cascade="all, delete-orphan")
    research_results = relationship("ResearchResult", back_populates="agent", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="agent", cascade="all, delete-orphan")
    test_results = relationship("AgentTestResult", back_populates="agent", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="agent", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="agent", cascade="all, delete-orphan")
    matches = relationship("AgentMatch", back_populates="agent", cascade="all, delete-orphan")
