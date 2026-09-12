"""Super Admin's platform-wide visibility into every Family, Buddy Group,
Church, and Fellowship - private to normal users, always visible here."""
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_admin
from app.models.user import User
from app.schemas.challenge import GroupAdminSummaryOut
from app.schemas.community import ChurchOut, FellowshipOut, ChurchUpdate, FellowshipUpdate
from app.services.challenge_service import ChallengeService
from app.services.community_service import CommunityService

router = APIRouter(prefix="/admin", tags=["Admin - Community"])


@router.get("/families", response_model=list[GroupAdminSummaryOut], summary="Every Family on the platform")
def list_all_families(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return ChallengeService(db).admin_list_all_groups("family")


@router.get("/buddy-groups", response_model=list[GroupAdminSummaryOut], summary="Every Buddy Group on the platform")
def list_all_buddy_groups(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return ChallengeService(db).admin_list_all_groups("buddy")


@router.get("/churches", response_model=list[ChurchOut], summary="Every Church on the platform")
def list_all_churches(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return CommunityService(db).admin_list_all_churches()


@router.get("/fellowships", response_model=list[FellowshipOut], summary="Every Fellowship on the platform")
def list_all_fellowships(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return CommunityService(db).admin_list_all_fellowships()


@router.patch("/churches/{church_id}", response_model=ChurchOut, summary="Edit any Church (Super Admin)")
def update_church(church_id: uuid.UUID, payload: ChurchUpdate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = CommunityService(db)
    church = svc.admin_update_church(current_user.id, church_id, payload)
    return svc._to_church_out(church, None)


@router.post("/churches/{church_id}/deactivate", response_model=ChurchOut, summary="Suspend a Church (Super Admin)")
def deactivate_church(church_id: uuid.UUID, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = CommunityService(db)
    church = svc.admin_set_church_status(current_user.id, church_id, "suspended")
    return svc._to_church_out(church, None)


@router.post("/churches/{church_id}/activate", response_model=ChurchOut, summary="Reactivate a suspended Church (Super Admin)")
def activate_church(church_id: uuid.UUID, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = CommunityService(db)
    church = svc.admin_set_church_status(current_user.id, church_id, "active")
    return svc._to_church_out(church, None)


@router.delete("/churches/{church_id}", summary="Permanently delete a Church and everything under it (Super Admin)")
def delete_church(church_id: uuid.UUID, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    CommunityService(db).admin_delete_church(current_user.id, church_id)
    return {"success": True}


@router.patch("/fellowships/{fellowship_id}", response_model=FellowshipOut, summary="Edit any Fellowship (Super Admin)")
def update_fellowship(fellowship_id: uuid.UUID, payload: FellowshipUpdate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = CommunityService(db)
    fellowship = svc.admin_update_fellowship(current_user.id, fellowship_id, payload)
    return svc._to_fellowship_out(fellowship, None)


@router.post("/fellowships/{fellowship_id}/deactivate", response_model=FellowshipOut, summary="Suspend a Fellowship (Super Admin)")
def deactivate_fellowship(fellowship_id: uuid.UUID, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = CommunityService(db)
    fellowship = svc.admin_set_fellowship_status(current_user.id, fellowship_id, "suspended")
    return svc._to_fellowship_out(fellowship, None)


@router.post("/fellowships/{fellowship_id}/activate", response_model=FellowshipOut, summary="Reactivate a suspended Fellowship (Super Admin)")
def activate_fellowship(fellowship_id: uuid.UUID, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = CommunityService(db)
    fellowship = svc.admin_set_fellowship_status(current_user.id, fellowship_id, "active")
    return svc._to_fellowship_out(fellowship, None)


@router.delete("/fellowships/{fellowship_id}", summary="Permanently delete a Fellowship (Super Admin)")
def delete_fellowship(fellowship_id: uuid.UUID, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    CommunityService(db).admin_delete_fellowship(current_user.id, fellowship_id)
    return {"success": True}
