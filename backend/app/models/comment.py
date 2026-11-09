import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_comment_id = Column(String(36), ForeignKey("comments.id", ondelete="SET NULL"), nullable=True, index=True)
    content = Column(Text, nullable=False)
    decision = Column(String(50), default="RESPOND")  # RESPOND, IGNORE, REQUEST_INFO
    reasoning = Column(Text, nullable=True)
    is_simulated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    post = relationship("Post", back_populates="comments")
    company = relationship("Company", back_populates="comments")
    agent = relationship("Agent", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")
