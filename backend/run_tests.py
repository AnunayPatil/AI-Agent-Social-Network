import sys
import os
import traceback
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from pydantic import ValidationError

from app.core.database import Base
from app.models.company import Company
from app.models.agent import Agent, AgentStatus
from app.models.post import Post
from app.models.comment import Comment
from app.models.conversation import Conversation
from app.models.notification import Notification
from app.schemas import (
    CompanyCreate,
    AgentTestRequest,
    ResearchRunRequest,
    PostCreate,
    CommentCreate,
    AgentRespondRequest
)

from app.api import (
    companies,
    agents,
    research,
    posts,
    matching,
    notifications,
    communication,
    analytics
)
from app.services.gemini_service import gemini_service
from app.services.research_service import research_service
from app.services.relevance_service import relevance_service
from app.services.langgraph_service import langgraph_service

# Isolated test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_runner.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def run_tests():
    print("=" * 70, flush=True)
    print("AI AGENT SOCIAL NETWORK - ENTERPRISE TEST SUITE", flush=True)
    print("=" * 70, flush=True)

    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()

    passed = 0
    failed = 0

    def test_case(name, fn):
        nonlocal passed, failed
        try:
            fn()
            print(f"  [PASS] {name}", flush=True)
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}", flush=True)
            traceback.print_exc()
            failed += 1

    # Test 1: Company Registration & Auto Agent Provisioning
    def t1():
        c_in = CompanyCreate(
            name="Swiggy",
            industry="Food Delivery",
            website_url="https://www.swiggy.com",
            description="Leading on-demand food delivery and quick commerce network in India.",
            products_services="Food Delivery, Swiggy Instamart, Dineout",
            business_objectives="Scale festival food orders, deepen payment partnerships.",
            target_audience="Urban consumers and food lovers across 500+ cities.",
            research_topics=["Food Delivery", "Festive Discounts", "Dining Deals"]
        )
        res = companies.register_company(c_in, db)
        assert res.name == "Swiggy"
        assert res.industry == "Food Delivery"

        # Verify Agent was automatically created and activated
        ag = db.query(Agent).filter(Agent.company_id == res.id).first()
        assert ag is not None
        assert ag.identity_name == "Swiggy AI Agent"
        assert ag.status == AgentStatus.ACTIVE
        assert "Swiggy" in ag.system_instructions

    test_case("Stage 1: Company Registration & Automatic Agent Provisioning", t1)

    # Test 2: Duplicate Company Registration Guard
    def t2():
        c_dup = CompanyCreate(
            name="Swiggy",
            industry="Food Delivery",
            website_url="https://www.swiggy.com",
            description="Duplicate registration attempt with valid length description.",
            products_services="Food Delivery & Groceries",
            business_objectives="Scale platform transactions",
            target_audience="Online Users"
        )
        try:
            companies.register_company(c_dup, db)
            assert False, "Should have raised HTTPException 400"
        except HTTPException as he:
            assert he.status_code == 400
            assert "already registered" in he.detail

    test_case("Stage 1: Duplicate Registration Prevention Guard", t2)

    # Test 3: Invalid Company Info (Pydantic validation)
    def t3():
        try:
            CompanyCreate(
                name="S",
                industry="",
                website_url="invalid",
                description="short",
                products_services="",
                business_objectives="",
                target_audience=""
            )
            assert False, "Should have failed Pydantic validation"
        except ValidationError:
            pass

    test_case("Stage 1: Pydantic Validation on Invalid Company Data", t3)

    # Test 4: Agent Comprehension Verification Test with Gemini
    def t4():
        ag = db.query(Agent).first()
        req = AgentTestRequest(custom_prompt="How do you handle merchant partnerships?")
        res = agents.run_agent_test(ag.id, req, db)
        assert res.passed is True
        assert res.score >= 0.70
        assert len(res.test_response) > 20

    test_case("Stage 1: Agent Comprehension Verification Test with Gemini", t4)

    # Test 5: Autonomous Web Research, Cleaning & Topic Classification
    def t5():
        ag = db.query(Agent).first()
        req = ResearchRunRequest(
            source_url_override="https://swiggy.com/news/festive-update",
            auto_generate_post=True
        )
        res = research.run_agent_research(ag.id, req, db)
        assert res.title
        assert res.cleaned_content
        assert len(res.extracted_topics) > 0
        assert res.post_id is not None

    test_case("Stage 2: Web Research Pipeline, Content Cleaning & Topic Extraction", t5)

    # Test 6: Duplicate Research Detection
    def t6():
        ag = db.query(Agent).first()
        req = ResearchRunRequest(
            source_url_override="https://swiggy.com/news/festive-update",
            auto_generate_post=False
        )
        res_dup = research.run_agent_research(ag.id, req, db)
        # Should detect existing content hash and return existing record without duplicating
        assert res_dup.id is not None

    test_case("Stage 2: Research Deduplication by Content Hash", t6)

    # Test 7: Post Creation, Like & Filter by Industry
    def t7():
        comp = db.query(Company).filter(Company.name == "Swiggy").first()
        ag = comp.agents[0]
        post_in = PostCreate(
            company_id=comp.id,
            agent_id=ag.id,
            title="Special Diwali offer: Get an additional 5% discount on food orders",
            content="Festive delights await! Order your favourite festive meals and enjoy extra 5% instant savings.",
            topic="Festive Dining",
            category="Offers",
            auto_trigger_matching=False
        )
        new_p = posts.create_post(post_in, db)
        assert new_p.title.startswith("Special Diwali offer")

        # Like post
        liked = posts.like_post(new_p.id, db)
        assert liked.likes_count == 1

        # Feed filter by industry
        feed_food = posts.get_social_feed(industry="Food Delivery", skip=0, limit=10, db=db)
        assert len(feed_food) >= 1
        assert feed_food[0].industry == "Food Delivery"

    test_case("Stage 2: Social Feed Publishing, Likes & Industry Filtering", t7)

    # Register partner companies for Stage 3: PhonePe, HDFC Bank, and Bajaj Auto
    def setup_partners():
        p_in = CompanyCreate(
            name="PhonePe",
            industry="Digital Payments",
            website_url="https://www.phonepe.com",
            description="India's leading UPI payments and merchant rewards platform.",
            products_services="UPI, Wallet, Merchant QR, Cashback Rewards",
            business_objectives="Maximize high-frequency transaction volume across food and shopping.",
            target_audience="Smartphone consumers across India.",
            research_topics=["Digital Payments", "UPI", "Merchant Cashback"]
        )
        companies.register_company(p_in, db)

        h_in = CompanyCreate(
            name="HDFC Bank",
            industry="Banking",
            website_url="https://www.hdfcbank.com",
            description="Leading private sector bank offering premium credit cards and retail dining benefits.",
            products_services="Credit Cards, Millennia Rewards, Merchant SmartBuy",
            business_objectives="Drive retail card spend on dining and merchant platforms.",
            target_audience="Affluent consumers and cardholders.",
            research_topics=["Credit Card Rewards", "Dining Offers", "Merchant Deals"]
        )
        companies.register_company(h_in, db)

        b_in = CompanyCreate(
            name="Bajaj Auto",
            industry="Automotive",
            website_url="https://www.bajajauto.com",
            description="Global two-wheeler manufacturer and electric scooter pioneer.",
            products_services="Motorcycles, Chetak EV Scooters",
            business_objectives="Expand EV urban mobility fleet.",
            target_audience="Two wheeler commuters and fleet buyers.",
            research_topics=["Electric Vehicles", "Automotive", "Battery Tech"]
        )
        companies.register_company(b_in, db)

    setup_partners()

    # Test 8: Relevance Matching Algorithm (Part A)
    def t8():
        swiggy_p = db.query(Post).filter(Post.title.ilike("%Diwali%")).first()
        matches = matching.trigger_matching(swiggy_p.id, threshold=0.55, db=db)
        matched_companies = [m.matched_company_name for m in matches]

        # Verify PhonePe and HDFC Bank matched
        assert "PhonePe" in matched_companies, f"PhonePe expected in {matched_companies}"
        assert "HDFC Bank" in matched_companies, f"HDFC Bank expected in {matched_companies}"

        # Verify Bajaj Auto (Automotive) is NOT matched (score < 0.55)
        assert "Bajaj Auto" not in matched_companies, f"Bajaj Auto should NOT match food post: {matched_companies}"

        # Verify Self-Match Prevention: Swiggy must NOT match its own post!
        assert "Swiggy" not in matched_companies

        # Verify reasons and scores
        for m in matches:
            assert m.relevance_score >= 0.55
            assert "Semantic similarity" in m.matching_reason

    test_case("Stage 3 Part A: Multi-Factor Relevance Matching & Anti-Self Match", t8)

    # Test 9: Notification System (Part B)
    def t9():
        swiggy_p = db.query(Post).filter(Post.title.ilike("%Diwali%")).first()
        phonepe_ag = db.query(Agent).join(Company).filter(Company.name == "PhonePe").first()
        
        notifs = notifications.get_agent_notifications(phonepe_ag.id, db)
        assert len(notifs) >= 1
        notif = notifs[0]
        assert notif.status in ["Delivered", "Pending", "Read", "Responded"]

        # Mark read
        read_res = notifications.mark_notification_read(notif.id, db)
        assert read_res.status == "Read"

    test_case("Stage 3 Part B: Notification Delivery, Inbox & Read Status", t9)

    # Test 10: LangGraph Autonomous Communication & Reciprocal Response (Part C)
    def t10():
        swiggy_p = db.query(Post).filter(Post.title.ilike("%Diwali%")).first()
        phonepe_ag = db.query(Agent).join(Company).filter(Company.name == "PhonePe").first()
        hdfc_ag = db.query(Agent).join(Company).filter(Company.name == "HDFC Bank").first()
        swiggy_ag = db.query(Agent).join(Company).filter(Company.name == "Swiggy").first()

        # PhonePe responds autonomously
        res_phonepe = communication.agent_autonomous_respond(
            phonepe_ag.id,
            AgentRespondRequest(post_id=swiggy_p.id),
            db
        )
        assert res_phonepe["decision"] == "RESPOND"
        assert res_phonepe["comment_content"] is not None

        # HDFC Bank responds autonomously
        res_hdfc = communication.agent_autonomous_respond(
            hdfc_ag.id,
            AgentRespondRequest(post_id=swiggy_p.id),
            db
        )
        assert res_hdfc["decision"] == "RESPOND"

        # Swiggy responds reciprocally
        res_swiggy = communication.agent_autonomous_respond(
            swiggy_ag.id,
            AgentRespondRequest(post_id=swiggy_p.id),
            db
        )
        assert res_swiggy["decision"] == "RESPOND"

        # Verify Conversation Thread
        conv = db.query(Conversation).filter(Conversation.post_id == swiggy_p.id).first()
        assert conv is not None
        assert conv.message_count >= 3
        assert conv.depth >= 2

        # Verify Duplicate Comment Prevention: PhonePe trying to comment again
        dup_res = communication.agent_autonomous_respond(
            phonepe_ag.id,
            AgentRespondRequest(post_id=swiggy_p.id),
            db
        )
        assert dup_res.get("is_duplicate") is True or dup_res["decision"] == "IGNORE"

    test_case("Stage 3 Part C: LangGraph Autonomous Multi-Agent Dialogue & Anti-Duplicate", t10)

    # Test 11: Conversation Controls & Pause State
    def t11():
        swiggy_p = db.query(Post).filter(Post.title.ilike("%Diwali%")).first()
        conv = db.query(Conversation).filter(Conversation.post_id == swiggy_p.id).first()
        
        # Pause conversation
        paused = communication.toggle_conversation_status(conv.id, "PAUSED", db)
        assert paused["status"] == "PAUSED"

        # Resume conversation
        resumed = communication.toggle_conversation_status(conv.id, "ACTIVE", db)
        assert resumed["status"] == "ACTIVE"

    test_case("Stage 3 Part C: Conversation Pause / Stop Controls", t11)

    # Test 12: Platform Analytics & Live KPIs
    def t12():
        m = analytics.get_system_metrics(db)
        assert m.total_companies >= 4 # Swiggy, PhonePe, HDFC Bank, Bajaj Auto
        assert m.total_agents >= 4
        assert m.active_agents >= 4
        assert m.total_posts >= 2
        assert m.total_notifications >= 2
        assert m.total_conversations >= 1

        activity = analytics.get_recent_activity(10, db)
        assert len(activity) > 0

    test_case("System: Real-Time Analytics & KPIs Aggregation", t12)

    db.close()
    Base.metadata.drop_all(bind=test_engine)

    print("=" * 70, flush=True)
    print(f"TEST EXECUTION SUMMARY: {passed} PASSED, {failed} FAILED", flush=True)
    print("=" * 70, flush=True)

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
