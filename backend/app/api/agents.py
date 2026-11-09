from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.agent import Agent, AgentStatus
from app.models.company import Company
from app.models.agent_config import AgentConfiguration
from app.models.test_result import AgentTestResult
from app.schemas import AgentResponse, AgentTestRequest, AgentTestResponse
from app.services.gemini_service import gemini_service
from app.services.research_service import research_service

router = APIRouter(prefix="/agents", tags=["Agents"])

def _build_agent_response(agent: Agent) -> AgentResponse:
    topics = agent.configuration.research_topics if agent.configuration and agent.configuration.research_topics else []
    threshold = agent.configuration.relevance_threshold if agent.configuration else 0.55
    is_paused = agent.configuration.is_paused if agent.configuration else False
    
    return AgentResponse(
        id=agent.id,
        company_id=agent.company_id,
        company_name=agent.company.name if agent.company else None,
        identity_name=agent.identity_name,
        role=agent.role,
        status=agent.status.value if hasattr(agent.status, 'value') else str(agent.status),
        system_instructions=agent.system_instructions,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
        research_topics=topics,
        relevance_threshold=threshold,
        is_paused=is_paused
    )

@router.get("", response_model=List[AgentResponse])
def list_agents(status: Optional[str] = None, db: Session = Depends(get_db)):
    """Lists all AI agents with status and configuration details."""
    query = db.query(Agent).join(Company, Agent.company_id == Company.id)
    if status:
        query = query.filter(Agent.status == status)
    agents = query.order_by(Agent.created_at.desc()).all()
    return [_build_agent_response(a) for a in agents]

@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Retrieves full agent details including system instructions and configuration."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return _build_agent_response(agent)

@router.post("/{agent_id}/test", response_model=AgentTestResponse)
def run_agent_test(agent_id: str, req: AgentTestRequest, db: Session = Depends(get_db)):
    """Runs an interactive or custom verification test on the agent's comprehension using Gemini."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    company = agent.company
    company_dict = {
        "name": company.name,
        "industry": company.industry,
        "description": company.description,
        "products_services": company.products_services,
        "business_objectives": company.business_objectives,
        "target_audience": company.target_audience
    }

    # Transition to testing temporarily
    prev_status = agent.status
    agent.status = AgentStatus.TESTING
    db.commit()

    test_data = gemini_service.verify_agent_comprehension(
        company_dict=company_dict,
        system_instructions=agent.system_instructions,
        custom_prompt=req.custom_prompt
    )

    test_result = AgentTestResult(
        agent_id=agent.id,
        test_type="custom_evaluation" if req.custom_prompt else "comprehension_and_persona",
        test_prompt=test_data["test_prompt"],
        test_response=test_data["test_response"],
        score=test_data["score"],
        passed=test_data["passed"],
        feedback=test_data["feedback"]
    )
    db.add(test_result)

    # Restore or upgrade status
    if test_result.passed and test_result.score >= 0.70:
        agent.status = AgentStatus.ACTIVE
    else:
        agent.status = AgentStatus.FAILED

    db.commit()
    db.refresh(test_result)
    return test_result

@router.get("/{agent_id}/tests", response_model=List[AgentTestResponse])
def get_agent_test_history(agent_id: str, db: Session = Depends(get_db)):
    """Fetches test history and verification benchmark results for an agent."""
    results = db.query(AgentTestResult).filter(AgentTestResult.agent_id == agent_id).order_by(AgentTestResult.created_at.desc()).all()
    return results

@router.post("/{agent_id}/activate", response_model=AgentResponse)
def activate_agent(agent_id: str, db: Session = Depends(get_db)):
    """Manually activates or enables an agent after review."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent.status = AgentStatus.ACTIVE
    db.commit()
    db.refresh(agent)
    return _build_agent_response(agent)

@router.post("/{agent_id}/toggle-pause", response_model=AgentResponse)
def toggle_agent_pause(agent_id: str, db: Session = Depends(get_db)):
    """Pauses or resumes autonomous participation for an agent."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if not agent.configuration:
        agent.configuration = AgentConfiguration(agent_id=agent.id)
    agent.configuration.is_paused = not agent.configuration.is_paused
    db.commit()
    db.refresh(agent)
    return _build_agent_response(agent)
