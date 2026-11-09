from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.company import Company
from app.models.agent import Agent
from app.schemas import CompanyCreate, CompanyResponse
from app.services.provisioning_service import provisioning_service

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.post("/register", response_model=CompanyResponse, status_code=201)
def register_company(company_in: CompanyCreate, db: Session = Depends(get_db)):
    """Registers a new company and automatically provisions, tests and activates its AI agent."""
    company, agent, test_result = provisioning_service.provision_company_and_agent(db, company_in)
    return CompanyResponse(
        id=company.id,
        name=company.name,
        industry=company.industry,
        website_url=company.website_url,
        description=company.description,
        products_services=company.products_services,
        business_objectives=company.business_objectives,
        target_audience=company.target_audience,
        research_topics=company.research_topics or [],
        avatar_url=company.avatar_url,
        created_at=company.created_at,
        agents_count=len(company.agents) if company.agents else 1
    )

@router.get("", response_model=List[CompanyResponse])
def list_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lists all registered companies with agent counts."""
    companies = db.query(Company).order_by(Company.created_at.desc()).offset(skip).limit(limit).all()
    res = []
    for c in companies:
        agent_count = db.query(func.count(Agent.id)).filter(Agent.company_id == c.id).scalar() or 0
        res.append(
            CompanyResponse(
                id=c.id,
                name=c.name,
                industry=c.industry,
                website_url=c.website_url,
                description=c.description,
                products_services=c.products_services,
                business_objectives=c.business_objectives,
                target_audience=c.target_audience,
                research_topics=c.research_topics or [],
                avatar_url=c.avatar_url,
                created_at=c.created_at,
                agents_count=agent_count
            )
        )
    return res

@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: str, db: Session = Depends(get_db)):
    """Retrieves full company details by ID."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    agent_count = db.query(func.count(Agent.id)).filter(Agent.company_id == company.id).scalar() or 0
    return CompanyResponse(
        id=company.id,
        name=company.name,
        industry=company.industry,
        website_url=company.website_url,
        description=company.description,
        products_services=company.products_services,
        business_objectives=company.business_objectives,
        target_audience=company.target_audience,
        research_topics=company.research_topics or [],
        avatar_url=company.avatar_url,
        created_at=company.created_at,
        agents_count=agent_count
    )
