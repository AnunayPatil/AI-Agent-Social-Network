import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "AI Agent Social Network")
    ENV: str = os.getenv("ENV", "development")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # Gemini AI API Configuration
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    GEMINI_EMBEDDING_MODEL: str = os.getenv("GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./agent_network.db")
    
    # Matching and Conversation Defaults
    DEFAULT_RELEVANCE_THRESHOLD: float = float(os.getenv("DEFAULT_RELEVANCE_THRESHOLD", "0.55"))
    MAX_CONVERSATION_DEPTH: int = int(os.getenv("MAX_CONVERSATION_DEPTH", "4"))
    MAX_RESPONSES_PER_POST: int = int(os.getenv("MAX_RESPONSES_PER_POST", "6"))
    AUTO_NOTIFY_AGENTS: bool = os.getenv("AUTO_NOTIFY_AGENTS", "true").lower() in ("true", "1", "yes")

settings = Settings()
