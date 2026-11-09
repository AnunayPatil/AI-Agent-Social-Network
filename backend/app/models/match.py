import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class AgentMatch(Base):
    __tablename__ = "agent_matches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    matched_agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    relevance_score = Column(Float, nullable=False)
    matching_reason = Column(Text, nullable=False)
    notification_status = Column(String(50), default="PENDING")  # PENDING, DELIVERED, READ, RESPONDED, IGNORED
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="matches")
    agent = relationship("Agent", back_populates="matches")
    notifications = relationship("Notification", back_populates="match", cascade="all, delete-orphan")
