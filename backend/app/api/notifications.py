from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.notification import Notification, NotificationStatus
from app.schemas import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])

def _build_notif_response(n: Notification) -> NotificationResponse:
    return NotificationResponse(
        id=n.id,
        recipient_agent_id=n.recipient_agent_id,
        recipient_agent_name=n.agent.identity_name if n.agent else "Agent",
        recipient_company_name=n.agent.company.name if n.agent and n.agent.company else "Company",
        post_id=n.post_id,
        post_title=n.post.title if n.post else "Post",
        match_id=n.match_id,
        title=n.title,
        message=n.message,
        status=n.status.value if hasattr(n.status, 'value') else str(n.status),
        created_at=n.created_at
    )

@router.get("", response_model=List[NotificationResponse])
def get_all_notifications(limit: int = 100, db: Session = Depends(get_db)):
    """Fetches global feed of all agent notifications."""
    notifs = db.query(Notification).order_by(Notification.created_at.desc()).limit(limit).all()
    return [_build_notif_response(n) for n in notifs]

@router.get("/{agent_id}", response_model=List[NotificationResponse])
def get_agent_notifications(agent_id: str, db: Session = Depends(get_db)):
    """Fetches inbox notifications for a specific agent."""
    notifs = db.query(Notification).filter(Notification.recipient_agent_id == agent_id).order_by(Notification.created_at.desc()).all()
    return [_build_notif_response(n) for n in notifs]

@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(notification_id: str, db: Session = Depends(get_db)):
    """Marks a notification as Read."""
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.status = NotificationStatus.READ
    db.commit()
    db.refresh(notif)
    return _build_notif_response(notif)
