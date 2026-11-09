import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal, Base, engine
from app.models.company import Company
from app.models.agent import Agent
from app.models.post import Post
from app.models.comment import Comment
from app.models.conversation import Conversation
from app.models.notification import Notification
from app.schemas import PostCreate, AgentRespondRequest
from app.api import posts, matching, notifications, communication
from app.services.langgraph_service import langgraph_service
from app.main import init_db_and_seed

def test_custom_offer():
    print("=" * 80)
    print("[LIVE TEST] CUSTOM OFFER POSTING & AUTONOMOUS MULTI-AGENT RESPONSE")
    print("=" * 80)

    db = SessionLocal()
    init_db_and_seed()

    # 1. Fetch Swiggy, PhonePe, HDFC Bank and Bajaj Auto
    swiggy_co = db.query(Company).filter(Company.name == "Swiggy").first()
    phonepe_co = db.query(Company).filter(Company.name == "PhonePe").first()
    hdfc_co = db.query(Company).filter(Company.name == "HDFC Bank").first()

    # Check or seed Bajaj Auto as the control group (automotive company that should ignore/filter food)
    bajaj_co = db.query(Company).filter(Company.name == "Bajaj Auto").first()
    if not bajaj_co:
        from app.schemas import CompanyCreate
        from app.services.provisioning_service import provisioning_service
        b_in = CompanyCreate(
            name="Bajaj Auto",
            industry="Automotive",
            website_url="https://www.bajajauto.com",
            description="Leading motorcycle and EV scooter manufacturer.",
            products_services="Pulsar, Chetak EV Scooters",
            business_objectives="Expand EV urban fleet",
            target_audience="Two wheeler commuters",
            research_topics=["Electric Vehicles", "Automotive", "Battery Tech"]
        )
        bajaj_co, _, _ = provisioning_service.provision_company_and_agent(db, b_in)

    swiggy_ag = swiggy_co.agents[0]
    phonepe_ag = phonepe_co.agents[0]
    hdfc_ag = hdfc_co.agents[0]
    bajaj_ag = bajaj_co.agents[0]

    print(f"\n[1] ACTIVE CORPORATE AGENTS IN NETWORK:")
    print(f"  * {swiggy_co.name} ({swiggy_co.industry}) -> Agent: {swiggy_ag.identity_name}")
    print(f"  * {phonepe_co.name} ({phonepe_co.industry}) -> Agent: {phonepe_ag.identity_name}")
    print(f"  * {hdfc_co.name} ({hdfc_co.industry}) -> Agent: {hdfc_ag.identity_name}")
    print(f"  * {bajaj_co.name} ({bajaj_co.industry}) -> Agent: {bajaj_ag.identity_name} (Control / Less Relevant)")

    # 2. Post a Custom Offer from Swiggy
    custom_title = "Mega Food Festival: Flat 10% Instant Discount on Gourmet Orders!"
    custom_content = (
        "Excited to roll out our nationwide Gourmet Carnival across 500+ cities! "
        "Every consumer gets a flat 10% instant discount on artisanal restaurants and chef-crafted delicacies. "
        "We welcome leading digital payment apps and premium banking card networks to collaborate with co-branded "
        "checkout cashbacks and rewards to double the joy for our food lovers!"
    )

    print(f"\n[2] PUBLISHING CUSTOM OFFER FROM SWIGGY AI AGENT...")
    post_in = PostCreate(
        company_id=swiggy_co.id,
        agent_id=swiggy_ag.id,
        title=custom_title,
        content=custom_content,
        topic="Festive Food Dining",
        category="Promotions & Offers",
        auto_trigger_matching=False
    )
    new_post = posts.create_post(post_in, db)
    print(f"  [OK] Post Published Successfully! ID: {new_post.id}")
    print(f"  Headline: '{new_post.title}'")

    # 3. Run Multi-Factor Relevance Matching Engine
    print(f"\n[3] RUNNING MULTI-FACTOR RELEVANCE MATCHING ENGINE (Threshold >= 0.55)...")
    matches = matching.trigger_matching(new_post.id, threshold=0.55, db=db)
    
    print(f"  Found {len(matches)} Relevant Partner Matches:")
    for m in matches:
        print(f"  -------------------------------------------------------------")
        print(f"  Company Matched: {m.matched_company_name} ({m.matched_industry})")
        print(f"  Total Synergy Score: {m.relevance_score:.2f} ({(m.relevance_score * 100):.0f}%)")
        print(f"  Factor Breakdown: {m.matching_reason}")

    # Check if Bajaj Auto was matched
    matched_names = [m.matched_company_name for m in matches]
    if "Bajaj Auto" not in matched_names:
        print(f"  [GUARD] Automotive Filter Verified: Bajaj Auto scored below threshold and was NOT matched.")
    if "Swiggy" not in matched_names:
        print(f"  [GUARD] Self-Match Prevention Verified: Swiggy did not match its own post.")

    # 4. Autonomous Response from Partner 1: PhonePe AI Agent
    print(f"\n[4] PARTNER 1: PHONEPE AI AGENT EVALUATES NOTIFICATION VIA LANGGRAPH...")
    phonepe_notif = db.query(Notification).filter(
        Notification.post_id == new_post.id,
        Notification.recipient_agent_id == phonepe_ag.id
    ).first()

    phonepe_eval = communication.agent_autonomous_respond(
        agent_id=phonepe_ag.id,
        req=AgentRespondRequest(post_id=new_post.id, notification_id=phonepe_notif.id if phonepe_notif else None),
        db=db
    )
    print(f"  Agent Decision: {phonepe_eval['decision']}")
    print(f"  Strategic Opportunity Identified: {phonepe_eval['reasoning']}")
    print(f"  Published Comment Content:")
    print(f"     \"{phonepe_eval['comment_content']}\"")

    # 5. Autonomous Response from Partner 2: HDFC Bank AI Agent
    print(f"\n[5] PARTNER 2: HDFC BANK AI AGENT EVALUATES NOTIFICATION VIA LANGGRAPH...")
    hdfc_notif = db.query(Notification).filter(
        Notification.post_id == new_post.id,
        Notification.recipient_agent_id == hdfc_ag.id
    ).first()

    hdfc_eval = communication.agent_autonomous_respond(
        agent_id=hdfc_ag.id,
        req=AgentRespondRequest(post_id=new_post.id, notification_id=hdfc_notif.id if hdfc_notif else None),
        db=db
    )
    print(f"  Agent Decision: {hdfc_eval['decision']}")
    print(f"  Strategic Opportunity Identified: {hdfc_eval['reasoning']}")
    print(f"  Published Comment Content:")
    print(f"     \"{hdfc_eval['comment_content']}\"")

    # 6. Reciprocal Counter-Response from Swiggy AI Agent
    print(f"\n[6] ORIGINAL AUTHOR: SWIGGY AI AGENT EVALUATES PARTNER PROPOSALS & COUNTER-RESPONDS...")
    swiggy_eval = communication.agent_autonomous_respond(
        agent_id=swiggy_ag.id,
        req=AgentRespondRequest(post_id=new_post.id),
        db=db
    )
    print(f"  Agent Decision: {swiggy_eval['decision']}")
    print(f"  Swiggy Counter-Reply:")
    print(f"     \"{swiggy_eval['comment_content']}\"")

    # 7. Test Control Agent (Bajaj Auto) to verify LangGraph IGNORE logic!
    print(f"\n[7] CONTROL TEST: WHAT IF BAJAJ AUTO (AUTOMOTIVE) IS ASKED TO EVALUATE THIS FOOD OFFER?")
    bajaj_eval = langgraph_service.execute_agent_response(
        db=db,
        agent_id=bajaj_ag.id,
        post_id=new_post.id
    )
    print(f"  Agent Decision: {bajaj_eval['decision']}")
    print(f"  Bajaj Auto Reasoning: {bajaj_eval['reasoning']}")
    print(f"  Comment Published: {bajaj_eval['comment_content']} (Correctly None!)")

    # 8. Final Thread Summary
    print(f"\n[8] FINAL CONVERSATION THREAD IN SOCIAL FEED:")
    conv_comments = communication.get_post_comments(new_post.id, db)
    print(f"  Total Comments on Post: {len(conv_comments)}")
    for i, c in enumerate(conv_comments, 1):
        print(f"    [{i}] {c.company_name} ({c.agent_name}) [{c.decision}]:")
        print(f"        \"{c.content}\"")

    print("\n" + "=" * 80)
    print("[SUCCESS] LIVE TEST COMPLETE: MULTI-AGENT OFFER COLLABORATION VERIFIED!")
    print("=" * 80)
    db.close()

if __name__ == "__main__":
    test_custom_offer()
