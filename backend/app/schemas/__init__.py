from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- COMPANY SCHEMAS ---
class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Official company name")
    industry: str = Field(..., min_length=2, max_length=100, description="Industry sector (e.g. Food Delivery, Digital Payments, Banking)")
    website_url: str = Field(..., description="Company official website URL")
    description: str = Field(..., min_length=10, description="Comprehensive company overview")
    products_services: str = Field(..., min_length=5, description="Core products and services offerings")
    business_objectives: str = Field(..., min_length=5, description="Key strategic and business objectives")
    target_audience: str = Field(..., min_length=5, description="Target customer segments and market")
    research_topics: List[str] = Field(default_factory=list, description="Topics and keywords the AI agent should monitor")
    avatar_url: Optional[str] = Field(None, description="Company logo or avatar URL")

class CompanyResponse(BaseModel):
    id: str
    name: str
    industry: str
    website_url: str
    description: str
    products_services: str
    business_objectives: str
    target_audience: str
    research_topics: List[str]
    avatar_url: Optional[str]
    created_at: datetime
    agents_count: Optional[int] = 0

    class Config:
        from_attributes = True

# --- AGENT SCHEMAS ---
class AgentResponse(BaseModel):
    id: str
    company_id: str
    company_name: Optional[str] = None
    identity_name: str
    role: str
    status: str
    system_instructions: str
    created_at: datetime
    updated_at: datetime
    research_topics: Optional[List[str]] = []
    relevance_threshold: Optional[float] = 0.55
    is_paused: Optional[bool] = False

    class Config:
        from_attributes = True

class AgentTestRequest(BaseModel):
    custom_prompt: Optional[str] = None

class AgentTestResponse(BaseModel):
    id: str
    agent_id: str
    test_type: str
    test_prompt: str
    test_response: str
    score: float
    passed: bool
    feedback: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- RESEARCH SCHEMAS ---
class ResearchRunRequest(BaseModel):
    query_override: Optional[str] = None
    source_url_override: Optional[str] = None
    auto_generate_post: bool = True

class ResearchResultResponse(BaseModel):
    id: str
    agent_id: str
    agent_name: Optional[str] = None
    source_url: str
    title: str
    cleaned_content: str
    extracted_topics: List[str]
    summary: str
    post_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# --- POST SCHEMAS ---
class PostCreate(BaseModel):
    company_id: str
    agent_id: str
    title: str = Field(..., min_length=3, max_length=500)
    content: str = Field(..., min_length=10)
    source_url: Optional[str] = None
    topic: Optional[str] = None
    category: Optional[str] = None
    is_simulated: bool = False
    auto_trigger_matching: bool = True

class PostResponse(BaseModel):
    id: str
    company_id: str
    company_name: str
    company_avatar: Optional[str]
    industry: str
    agent_id: str
    agent_name: str
    title: str
    content: str
    source_url: Optional[str]
    topic: Optional[str]
    category: Optional[str]
    likes_count: int
    comments_count: int
    matched_count: int
    is_simulated: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- MATCH SCHEMAS ---
class AgentMatchResponse(BaseModel):
    id: str
    post_id: str
    matched_agent_id: str
    matched_company_name: str
    matched_agent_name: str
    matched_industry: str
    relevance_score: float
    matching_reason: str
    notification_status: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- NOTIFICATION SCHEMAS ---
class NotificationResponse(BaseModel):
    id: str
    recipient_agent_id: str
    recipient_agent_name: Optional[str]
    recipient_company_name: Optional[str]
    post_id: str
    post_title: Optional[str]
    match_id: Optional[str]
    title: str
    message: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- COMMENT & CONVERSATION SCHEMAS ---
class CommentCreate(BaseModel):
    company_id: str
    agent_id: str
    content: str
    parent_comment_id: Optional[str] = None
    decision: str = "RESPOND"
    reasoning: Optional[str] = None

class CommentResponse(BaseModel):
    id: str
    post_id: str
    company_id: str
    company_name: str
    company_avatar: Optional[str]
    agent_id: str
    agent_name: str
    parent_comment_id: Optional[str]
    content: str
    decision: str
    reasoning: Optional[str]
    is_simulated: bool
    created_at: datetime
    replies: Optional[List['CommentResponse']] = []

    class Config:
        from_attributes = True

class AgentRespondRequest(BaseModel):
    post_id: str
    notification_id: Optional[str] = None
    override_decision: Optional[str] = None  # None for autonomous LLM evaluation

class ConversationResponse(BaseModel):
    id: str
    post_id: str
    post_title: str
    original_company: str
    original_agent: str
    participating_agents: List[Dict[str, str]]
    message_count: int
    depth: int
    status: str
    created_at: datetime
    updated_at: datetime
    comments: List[CommentResponse]

    class Config:
        from_attributes = True

# --- ANALYTICS SCHEMAS ---
class MetricsResponse(BaseModel):
    total_companies: int
    total_agents: int
    active_agents: int
    total_research: int
    total_posts: int
    total_notifications: int
    total_conversations: int
