import uuid

from sqlalchemy.orm import Session

from app.models.misc import AuditLog


def record(db: Session, actor_id: uuid.UUID | None, action: str, entity_type: str, entity_id: uuid.UUID | None = None, metadata: dict | None = None) -> None:
    db.add(AuditLog(actor_id=actor_id, action=action, entity_type=entity_type, entity_id=entity_id, log_metadata=metadata))
