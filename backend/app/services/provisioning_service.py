import logging
from typing import Tuple, Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.company import Company
from app.models.agent import Agent, AgentStatus
from app.models.agent_config import AgentConfiguration
from app.models.research import ResearchSource
from app.models.test_result import AgentTestResult
from app.schemas import CompanyCreate
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

class ProvisioningService:
    def provision_company_and_agent(self, db: Session, company_in: CompanyCreate) -> Tuple[Company, Agent, AgentTestResult]:
        """Orchestrates automatic Stage 1 enterprise provisioning."""
        # 1. Duplicate check
        existing_company = db.query(Company).filter(Company.name.ilike(company_in.name.strip())).first()
        if existing_company:
            raise HTTPException(
                status_code=400,
                detail=f"Company with name '{company_in.name}' is already registered."
            )

        # 2. Save Company Information in database
        company = Company(
            name=company_in.name.strip(),
            industry=company_in.industry.strip(),
            website_url=str(company_in.website_url).strip(),
            description=company_in.description.strip(),
            products_services=company_in.products_services.strip(),
            business_objectives=company_in.business_objectives.strip(),
            target_audience=company_in.target_audience.strip(),
            research_topics=company_in.research_topics or [company_in.industry, "Innovation", "Partnerships"],
            avatar_url=company_in.avatar_url or f"https://api.dicebear.com/7.x/identicon/svg?seed={company_in.name}"
        )
        db.add(company)
        db.flush()

        # 3. Create Dedicated AI Agent & Unique Identity
        identity_name = f"{company.name} AI Agent"
        agent = Agent(
            company_id=company.id,
            identity_name=identity_name,
            role="Autonomous Corporate Brand & Strategic Intelligence Agent",
            status=AgentStatus.PENDING,
            system_instructions=""
        )
        db.add(agent)
        db.flush()

        # 4. Generate Company-Specific System Instructions via Gemini
        company_dict = {
            "name": company.name,
            "industry": company.industry,
            "website_url": company.website_url,
            "description": company.description,
            "products_services": company.products_services,
            "business_objectives": company.business_objectives,
            "target_audience": company.target_audience,
            "research_topics": company.research_topics
        }
        system_instructions, is_simulated = gemini_service.generate_system_instructions(company_dict)
        agent.system_instructions = system_instructions

        # 5. Configure Research Topics and Sources
        default_sources = [
            ResearchSource(
                agent_id=agent.id,
                source_type="COMPANY_WEBSITE",
                name=f"{company.name} Official Portal",
                url=company.website_url,
                is_active=True
            ),
            ResearchSource(
                agent_id=agent.id,
                source_type="RSS",
                name=f"{company.industry} Market Wire",
                url=f"https://news.google.com/rss/search?q={company.name}+{company.industry}",
                is_active=True
            )
        ]
        for src in default_sources:
            db.add(src)

        agent_config = AgentConfiguration(
            agent_id=agent.id,
            research_topics=company.research_topics,
            research_sources=[s.url for s in default_sources],
            auto_publish=True,
            relevance_threshold=0.55,
            max_response_depth=4,
            is_paused=False
        )
        db.add(agent_config)

        # 6. Status -> Testing
        agent.status = AgentStatus.TESTING
        db.flush()

        # 7 & 8. Run Automatic Agent Verification Test with Gemini
        test_data = gemini_service.verify_agent_comprehension(
            company_dict=company_dict,
            system_instructions=agent.system_instructions
        )

        test_result = AgentTestResult(
            agent_id=agent.id,
            test_type="comprehension_and_persona",
            test_prompt=test_data["test_prompt"],
            test_response=test_data["test_response"],
            score=test_data["score"],
            passed=test_data["passed"],
            feedback=test_data["feedback"]
        )
        db.add(test_result)

        # 9. Activate Agent after successful testing
        if test_result.passed and test_result.score >= 0.70:
            agent.status = AgentStatus.ACTIVE
            logger.info(f"Agent {agent.identity_name} successfully verified and activated!")
        else:
            agent.status = AgentStatus.FAILED
            logger.warning(f"Agent {agent.identity_name} failed comprehension test.")

        db.commit()
        db.refresh(company)
        db.refresh(agent)
        db.refresh(test_result)

        return company, agent, test_result

provisioning_service = ProvisioningService()
