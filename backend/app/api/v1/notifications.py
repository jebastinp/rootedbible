import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationOut
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationOut], summary="My notifications, newest first")
def list_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return NotificationService(db).list_mine(current_user.id)


@router.get("/unread-count", summary="Count of unread notifications")
def unread_count(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"count": NotificationService(db).unread_count(current_user.id)}


@router.post("/{notification_id}/read", summary="Mark one notification read")
def mark_read(notification_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    NotificationService(db).mark_read(current_user.id, notification_id)
    return {"success": True}


@router.post("/read-all", summary="Mark all my notifications read")
def mark_all_read(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    NotificationService(db).mark_all_read(current_user.id)
    return {"success": True}
