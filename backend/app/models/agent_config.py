import uuid
from sqlalchemy import Column, String, Boolean, Float, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class AgentConfiguration(Base):
    __tablename__ = "agent_configurations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), unique=True, nullable=False)
    research_topics = Column(JSON, default=list)
    research_sources = Column(JSON, default=list)
    auto_publish = Column(Boolean, default=True)
    relevance_threshold = Column(Float, default=0.55)
    max_response_depth = Column(Integer, default=4)
    is_paused = Column(Boolean, default=False)

    agent = relationship("Agent", back_populates="configuration")
