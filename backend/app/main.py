import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
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
from app.models.company import Company
from app.schemas import CompanyCreate
from app.services.provisioning_service import provisioning_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("agent_network")

def init_db_and_seed():
    """Initializes tables and seeds initial demo companies synchronously."""
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        sample_companies = [
            CompanyCreate(
                name="Swiggy",
                industry="Food Delivery",
                website_url="https://www.swiggy.com",
                description="India's leading on-demand convenience platform connecting consumers with tens of thousands of restaurants, cloud kitchens, and daily essentials via Instamart.",
                products_services="Food Delivery, Swiggy Instamart, Dineout, Swiggy One membership",
                business_objectives="Accelerate high-frequency customer ordering, scale festival dining campaigns, and partner with fintechs to drive checkout affordability.",
                target_audience="Urban food lovers, millennials, busy professionals, and families seeking instant dining and grocery delivery.",
                research_topics=["Food Delivery", "Festive Offers", "Restaurant Deals", "Quick Commerce", "Dining Trends"],
                avatar_url="https://images.unsplash.com/photo-1526367790999-0150786686a2?w=120&h=120&fit=crop"
            ),
            CompanyCreate(
                name="PhonePe",
                industry="Digital Payments",
                website_url="https://www.phonepe.com",
                description="India's premier digital payments and fintech conglomerate facilitating bill payments, peer-to-peer transfers, merchant checkouts, and financial investments.",
                products_services="UPI Payments, PhonePe Wallet, QR Code Solutions, Merchant Rewards, Credit on UPI",
                business_objectives="Maximize digital transaction volume, foster merchant partner cashback initiatives, and cement checkout leadership across e-commerce and food apps.",
                target_audience="Over 500 million registered smartphone users and 35+ million merchant stores across metro and regional India.",
                research_topics=["Digital Payments", "UPI Innovations", "Merchant Cashback", "Fintech Loyalty", "Payment Security"],
                avatar_url="https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=120&h=120&fit=crop"
            ),
            CompanyCreate(
                name="HDFC Bank",
                industry="Banking",
                website_url="https://www.hdfcbank.com",
                description="India's leading private sector banking and financial services institution delivering comprehensive retail banking, card portfolios, and commercial financing.",
                products_services="Credit Cards, Millennia & Regalia Dining Rewards, SmartBuy Merchant Portal, Consumer Loans",
                business_objectives="Drive cardholder retail spends across lifestyle categories, expand merchant promotional partnerships, and deliver premium rewards.",
                target_audience="Salaried professionals, affluent consumers, and entrepreneurs seeking reliable banking and high-value rewards.",
                research_topics=["Credit Card Rewards", "Consumer Banking", "Digital Lending", "Festive Spends", "Merchant Offers"],
                avatar_url="https://images.unsplash.com/photo-1541354329998-f4d9a9f9297f?w=120&h=120&fit=crop"
            )
        ]

        for sc in sample_companies:
            existing = db.query(Company).filter(Company.name == sc.name).first()
            if not existing:
                company, agent, test_res = provisioning_service.provision_company_and_agent(db, sc)
                logger.info(f"Seeded company {company.name} with AI Agent {agent.identity_name}")
        db.close()
    except Exception as e:
        logger.error(f"Error initializing DB: {e}")

# Run DB sync init
init_db_and_seed()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    yield
    logger.info("Application shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A Social Networking Platform for Autonomous Enterprise AI Agents",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(companies.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(research.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(matching.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(communication.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "demo_mode": settings.DEMO_MODE,
        "database": settings.DATABASE_URL.split("://")[0]
    }
