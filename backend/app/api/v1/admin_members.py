import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_super_admin
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserOut, UserCreate, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/admin/members", tags=["Admin - Members"])


@router.get("", summary="List members (search, filter by role/status, paginated)")
def list_members(
    search: str | None = None,
    role: UserRole | None = None,
    status_filter: UserStatus | None = Query(default=None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    items, total = UserService(db).list(search, role, status_filter, page, page_size)
    return {
        "items": [UserOut.model_validate(u) for u in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("", response_model=UserOut, summary="Add a new member")
def create_member(payload: UserCreate, db: Session = Depends(get_db), _: User = Depends(require_super_admin)):
    return UserService(db).create(payload)


@router.get("/{member_id}", response_model=UserOut, summary="Get a single member")
def get_member(member_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_super_admin)):
    return UserService(db).get(member_id)


@router.patch("/{member_id}", response_model=UserOut, summary="Edit a member")
def update_member(member_id: uuid.UUID, payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_super_admin)):
    return UserService(db).update(member_id, payload, actor_id=current_user.id)


@router.post("/{member_id}/deactivate", response_model=UserOut, summary="Deactivate a member")
def deactivate_member(member_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_super_admin)):
    return UserService(db).deactivate(member_id, actor_id=current_user.id)


@router.post("/{member_id}/activate", response_model=UserOut, summary="Reactivate a member")
def activate_member(member_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_super_admin)):
    return UserService(db).activate(member_id, actor_id=current_user.id)


@router.delete("/{member_id}", summary="Soft-delete a member")
def delete_member(member_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_super_admin)):
    UserService(db).delete(member_id, actor_id=current_user.id)
    return {"message": "Member deleted successfully"}
