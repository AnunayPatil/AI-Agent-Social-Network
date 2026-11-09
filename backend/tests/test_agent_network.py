import pytest
import warnings
warnings.filterwarnings('ignore')
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.models.company import Company
from app.models.agent import Agent, AgentStatus
from app.models.post import Post
from app.models.comment import Comment
from app.models.conversation import Conversation
from app.services.gemini_service import gemini_service
from app.services.research_service import research_service
from app.services.relevance_service import relevance_service

# Test SQLite in-memory database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_agent_network.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def client():
    return TestClient(app)

# 1. Company Registration & Duplicate Check
def test_company_registration(client):
    payload = {
        "name": "Flipkart",
        "industry": "E-Commerce",
        "website_url": "https://www.flipkart.com",
        "description": "India's homegrown e-commerce marketplace offering over 150M products.",
        "products_services": "Online Retail, SuperCoins, Flipkart Pay Later",
        "business_objectives": "Maximize shopping festival sales and scale payment partner rewards.",
        "target_audience": "Online consumers across metro, tier-2 and tier-3 cities.",
        "research_topics": ["E-Commerce", "Big Billion Days", "Consumer Tech"]
    }
    resp = client.post("/api/companies/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Flipkart"
    assert data["industry"] == "E-Commerce"

def test_duplicate_company_registration(client):
    payload = {
        "name": "Flipkart",
        "industry": "E-Commerce",
        "website_url": "https://www.flipkart.com",
        "description": "Duplicate test registration attempt.",
        "products_services": "Retail",
        "business_objectives": "Scale",
        "target_audience": "Shoppers"
    }
    resp = client.post("/api/companies/register", json=payload)
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"]

def test_invalid_company_information(client):
    payload = {
        "name": "F", # Too short
        "industry": "E",
        "website_url": "https://flipkart.com",
        "description": "Short",
        "products_services": "",
        "business_objectives": "",
        "target_audience": ""
    }
    resp = client.post("/api/companies/register", json=payload)
    assert resp.status_code == 422 # Pydantic validation error

# 2. Automatic Agent Creation & Status
def test_automatic_agent_creation(client):
    resp = client.get("/api/agents")
    assert resp.status_code == 200
    agents = resp.json()
    flipkart_agent = next((a for a in agents if "Flipkart" in a["identity_name"]), None)
    assert flipkart_agent is not None
    assert flipkart_agent["status"] == "Active"
    assert "Flipkart" in flipkart_agent["system_instructions"]

# 3. Agent Testing
def test_agent_custom_test(client):
    agents = client.get("/api/agents").json()
    agent_id = agents[0]["id"]
    test_payload = {"custom_prompt": "Explain your brand strategy for ecosystem collaborations."}
    resp = client.post(f"/api/agents/{agent_id}/test", json=test_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["passed"] is True
    assert data["score"] >= 0.70

# 4. Web Research Pipeline & Deduplication
def test_research_pipeline_and_deduplication(client):
    agents = client.get("/api/agents").json()
    agent_id = agents[0]["id"]
    
    # Run research first time
    req1 = {"source_url_override": "https://news.ycombinator.com", "auto_generate_post": True}
    resp1 = client.post(f"/api/research/{agent_id}/run", json=req1)
    assert resp1.status_code == 200
    res1 = resp1.json()
    assert res1["title"]
    assert res1["cleaned_content"]

    # Run again with same content -> should detect duplicate
    resp2 = client.post(f"/api/research/{agent_id}/run", json=req1)
    assert resp2.status_code == 200
    res2 = resp2.json()
    assert res2["id"] == res1["id"]

# 5. Post Publishing & Social Feed
def test_post_creation_and_feed(client):
    comps = client.get("/api/companies").json()
    agents = client.get("/api/agents").json()
    
    post_payload = {
        "company_id": comps[0]["id"],
        "agent_id": agents[0]["id"],
        "title": "Unveiling Next-Gen Payment Checkouts",
        "content": "Delighted to announce our seamless API gateway for retail partners across India.",
        "topic": "Digital Payments",
        "category": "Product Launch",
        "auto_trigger_matching": True
    }
    resp = client.post("/api/posts", json=post_payload)
    assert resp.status_code == 201
    post_id = resp.json()["id"]

    # Retrieve feed
    feed = client.get("/api/posts").json()
    assert len(feed) > 0
    assert any(p["id"] == post_id for p in feed)

    # Like post
    like_resp = client.post(f"/api/posts/{post_id}/like")
    assert like_resp.status_code == 200
    assert like_resp.json()["likes_count"] == 1

# 6. Relevance Matching & Self-Matching Prevention
def test_relevance_matching_and_self_match_prevention(client):
    # Register Swiggy & TVS Motors
    swiggy_p = {
        "name": "Swiggy Test",
        "industry": "Food Delivery",
        "website_url": "https://swiggy.test",
        "description": "Food delivery app",
        "products_services": "Food Delivery",
        "business_objectives": "Scale discount campaigns with fintech partners",
        "target_audience": "Consumers",
        "research_topics": ["Food", "Discounts"]
    }
    client.post("/api/companies/register", json=swiggy_p)

    tvs_p = {
        "name": "TVS Motors Test",
        "industry": "Automotive",
        "website_url": "https://tvsmotor.test",
        "description": "Two wheeler vehicle manufacturer",
        "products_services": "Scooters",
        "business_objectives": "Manufacture electric bikes",
        "target_audience": "Commuters",
        "research_topics": ["EV", "Automotive"]
    }
    client.post("/api/companies/register", json=tvs_p)

    agents = client.get("/api/agents").json()
    swiggy_ag = next(a for a in agents if "Swiggy Test" in a["identity_name"])
    tvs_ag = next(a for a in agents if "TVS Motors Test" in a["identity_name"])

    post_resp = client.post("/api/posts", json={
        "company_id": swiggy_ag["company_id"],
        "agent_id": swiggy_ag["id"],
        "title": "Diwali Food Offer: 5% Extra Off",
        "content": "Special festive discount on gourmet food orders with bank payment options.",
        "auto_trigger_matching": True
    })
    post_id = post_resp.json()["id"]

    # Match post
    matches_resp = client.post(f"/api/matching/{post_id}")
    assert matches_resp.status_code == 200
    matches = matches_resp.json()

    # Self-matching check: Swiggy must NOT match its own post!
    for m in matches:
        assert m["matched_agent_id"] != swiggy_ag["id"]

# 7. LangGraph Autonomous Communication & Duplicate Comment Guard
def test_langgraph_autonomous_communication(client):
    posts = client.get("/api/posts").json()
    post_id = posts[0]["id"]
    agents = client.get("/api/agents").json()
    candidate_agent = [a for a in agents if a["company_id"] != posts[0]["company_id"]][0]

    # Execute agent respond
    resp = client.post(f"/api/agents/{candidate_agent['id']}/respond", json={"post_id": post_id})
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["decision"] in ["RESPOND", "IGNORE", "REQUEST_INFO"]

    # Test Duplicate prevention: calling again should prevent duplicate comment!
    resp_dup = client.post(f"/api/agents/{candidate_agent['id']}/respond", json={"post_id": post_id})
    assert resp_dup.status_code == 200
    assert resp_dup.json().get("is_duplicate") is True or resp_dup.json()["decision"] == "IGNORE"

# 8. Analytics & Metrics
def test_analytics_metrics(client):
    resp = client.get("/api/analytics/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_companies"] >= 1
    assert data["total_agents"] >= 1
    assert data["active_agents"] >= 1
