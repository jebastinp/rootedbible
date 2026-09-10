"""Super Admin's platform-wide visibility into every Family, Buddy Group,
Church, and Fellowship - private to normal users, always visible here."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_admin
from app.models.user import User
from app.schemas.challenge import GroupAdminSummaryOut
from app.schemas.community import ChurchOut, FellowshipOut
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
