import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base, JSONVector

class PostEmbedding(Base):
    __tablename__ = "post_embeddings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=True, index=True)
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=True, index=True)
    target_type = Column(String(50), default="POST")  # POST, AGENT_PROFILE, COMPANY
    embedding_vector = Column(JSONVector, nullable=False)
    dimension = Column(Integer, default=768)
    model_name = Column(String(100), default="models/text-embedding-004")
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="embeddings")
