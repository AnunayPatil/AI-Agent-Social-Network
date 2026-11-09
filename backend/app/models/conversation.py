import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), unique=True, nullable=False)
    participating_agent_ids = Column(JSON, default=list)  # list of agent UUIDs
    message_count = Column(Integer, default=0)
    depth = Column(Integer, default=0)
    status = Column(String(50), default="ACTIVE")  # ACTIVE, PAUSED, CLOSED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    post = relationship("Post", back_populates="conversation")
