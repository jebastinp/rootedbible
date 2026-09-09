import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_admin
from app.models.user import User
from app.models.misc import AuditLog

router = APIRouter(prefix="/admin/audit-logs", tags=["Admin - Audit Logs"])


class AuditLogOut(BaseModel):
    id: uuid.UUID
    actor_id: uuid.UUID | None = None
    actor_name: str | None = None
    action: str
    entity_type: str
    entity_id: uuid.UUID | None = None
    metadata: dict | None = None
    created_at: datetime


@router.get("", response_model=list[AuditLogOut], summary="Recent admin/audit activity")
def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    rows = (
        db.query(AuditLog, User)
        .outerjoin(User, User.id == AuditLog.actor_id)
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return [
        AuditLogOut(
            id=log.id, actor_id=log.actor_id, actor_name=user.name if user else None, action=log.action,
            entity_type=log.entity_type, entity_id=log.entity_id, metadata=log.log_metadata, created_at=log.created_at,
        )
        for log, user in rows
    ]
