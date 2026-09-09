import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_admin, require_super_admin, get_current_user
from app.core.exceptions import ConflictError
from app.models.user import User
from app.schemas.misc import (
    AnnouncementOut, AnnouncementCreate, AnnouncementUpdate,
    ChurchSettingsOut, ChurchSettingsUpdate,
)
from app.schemas.user import AdminAccountEmailUpdate, UserOut
from app.services.announcement_service import AnnouncementService, SettingsService
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/admin", tags=["Admin - Announcements & Settings"])


@router.get("/announcements", summary="List all announcements (admin)")
def list_announcements(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    items, total = AnnouncementService(db).list_all(page, page_size)
    return {"items": [AnnouncementOut.model_validate(a) for a in items], "total": total, "page": page, "page_size": page_size}


@router.post("/announcements", response_model=AnnouncementOut, summary="Create an announcement")
def create_announcement(payload: AnnouncementCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return AnnouncementService(db).create(payload, created_by=current_user.id)


@router.patch("/announcements/{announcement_id}", response_model=AnnouncementOut, summary="Edit an announcement")
def update_announcement(announcement_id: uuid.UUID, payload: AnnouncementUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return AnnouncementService(db).update(announcement_id, payload)


@router.delete("/announcements/{announcement_id}", summary="Delete an announcement")
def delete_announcement(announcement_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    AnnouncementService(db).delete(announcement_id)
    return {"message": "Announcement deleted successfully"}


@router.get("/settings", response_model=ChurchSettingsOut, summary="Get church settings")
def get_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return SettingsService(db).get()


@router.patch("/settings", response_model=ChurchSettingsOut, summary="Update church settings")
def update_settings(payload: ChurchSettingsUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return SettingsService(db).update(payload)


@router.patch("/account/email", response_model=UserOut, summary="Set the Super Admin's own sign-in email")
def update_admin_email(
    payload: AdminAccountEmailUpdate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    email = payload.email.strip().lower()
    users = UserRepository(db)
    existing = users.get_by_email(email)
    if existing and existing.id != current_user.id:
        raise ConflictError("Another account already uses this email.")
    updated = users.update(current_user, email=email)
    return UserOut.model_validate(updated)
