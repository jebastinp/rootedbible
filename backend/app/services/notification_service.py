import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.notification import Notification


def notify(db: Session, user_id: uuid.UUID, type: str, title: str, message: str | None = None, link: str | None = None) -> None:
    """Fire-and-forget: adds to the session but does not commit - callers
    already commit as part of their own transaction (join request, approval,
    etc.), so a notification never needs its own separate commit."""
    db.add(Notification(user_id=user_id, type=type, title=title, message=message, link=link))


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def list_mine(self, user_id: uuid.UUID, limit: int = 50) -> list[Notification]:
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )

    def unread_count(self, user_id: uuid.UUID) -> int:
        return self.db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read.is_(False)).count()

    def mark_read(self, user_id: uuid.UUID, notification_id: uuid.UUID) -> None:
        notification = self.db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_id).first()
        if not notification:
            raise NotFoundError("Notification not found.")
        notification.is_read = True
        self.db.commit()

    def mark_all_read(self, user_id: uuid.UUID) -> None:
        self.db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read.is_(False)).update({"is_read": True})
        self.db.commit()
