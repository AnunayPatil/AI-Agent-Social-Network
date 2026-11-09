import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class AgentTestResult(Base):
    __tablename__ = "agent_test_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    test_type = Column(String(100), default="comprehension_and_persona")
    test_prompt = Column(Text, nullable=False)
    test_response = Column(Text, nullable=False)
    score = Column(Float, nullable=False)  # 0.0 to 1.0
    passed = Column(Boolean, default=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="test_results")
