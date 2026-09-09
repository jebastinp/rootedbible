import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_admin
from app.models.user import User
from app.schemas.challenge import (
    ChallengeCreate, ChallengeUpdate, ChallengeAdminOut, GroupDetailOut,
    RewardCreate, RewardOut, ChallengeMemberAdminOut, ChallengeRequestAdminOut,
)
from app.services.challenge_service import ChallengeService

router = APIRouter(prefix="/admin/challenges", tags=["Admin - Church Challenges"])


@router.get("", response_model=list[ChallengeAdminOut], summary="List all Church Challenges")
def list_challenges(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return ChallengeService(db).admin_list_challenges()


@router.post("", response_model=ChallengeAdminOut, summary="Create a Church Challenge")
def create_challenge(payload: ChallengeCreate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    challenge = ChallengeService(db).admin_create_challenge(current_user.id, payload)
    return _to_admin_out(db, challenge)


def _to_admin_out(db: Session, challenge) -> ChallengeAdminOut:
    svc = ChallengeService(db)
    return ChallengeAdminOut(
        id=challenge.id, name=challenge.name, church_name=challenge.church_name, description=challenge.description,
        reading_plan_id=challenge.reading_plan_id, start_date=challenge.start_date, end_date=challenge.end_date,
        participant_limit=challenge.participant_limit, participant_count=svc._participant_count(challenge.id),
        status=challenge.status, allow_families=challenge.allow_families, family_limit=challenge.family_limit,
        allow_buddies=challenge.allow_buddies, buddy_limit=challenge.buddy_limit, quiz_enabled=challenge.quiz_enabled,
        rewards_enabled=challenge.rewards_enabled, created_at=challenge.created_at,
    )


@router.patch("/{challenge_id}", response_model=ChallengeAdminOut, summary="Update a Church Challenge")
def update_challenge(challenge_id: uuid.UUID, payload: ChallengeUpdate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    challenge = ChallengeService(db).admin_update_challenge(current_user.id, challenge_id, payload)
    return _to_admin_out(db, challenge)


@router.delete("/{challenge_id}", summary="Archive a Church Challenge")
def delete_challenge(challenge_id: uuid.UUID, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    ChallengeService(db).admin_delete_challenge(current_user.id, challenge_id)
    return {"success": True}


@router.post("/requests/{request_id}/approve", summary="Approve a pending challenge join request")
def approve_member(request_id: uuid.UUID, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    ChallengeService(db).admin_approve_challenge_member(current_user.id, request_id, approve=True)
    return {"success": True}


@router.post("/requests/{request_id}/decline", summary="Decline a pending challenge join request")
def decline_member(request_id: uuid.UUID, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    ChallengeService(db).admin_approve_challenge_member(current_user.id, request_id, approve=False)
    return {"success": True}


@router.delete("/{challenge_id}/members/{rooted_id}", summary="Remove a participant from the challenge")
def remove_member(challenge_id: uuid.UUID, rooted_id: str, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    ChallengeService(db).admin_remove_challenge_member(current_user.id, challenge_id, rooted_id)
    return {"success": True}


@router.get("/{challenge_id}/pending-requests", response_model=list[ChallengeRequestAdminOut], summary="Pending join requests for this challenge")
def list_pending_requests(challenge_id: uuid.UUID, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return ChallengeService(db).admin_list_pending_requests(challenge_id)


@router.get("/{challenge_id}/members", response_model=list[ChallengeMemberAdminOut], summary="List active participants with progress/streak")
def list_challenge_members(challenge_id: uuid.UUID, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return ChallengeService(db).admin_list_challenge_members(challenge_id)


@router.get("/{challenge_id}/families", response_model=list[GroupDetailOut], summary="List all families in this challenge")
def list_families(challenge_id: uuid.UUID, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    from app.models.challenge import Family
    svc = ChallengeService(db)
    families = db.query(Family).filter(Family.challenge_id == challenge_id).all()
    return [svc.get_group_detail("family", family.owner_id, family.id) for family in families]


@router.get("/{challenge_id}/buddy-groups", response_model=list[GroupDetailOut], summary="List all buddy groups in this challenge")
def list_buddy_groups(challenge_id: uuid.UUID, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    from app.models.challenge import BuddyGroup
    svc = ChallengeService(db)
    groups = db.query(BuddyGroup).filter(BuddyGroup.challenge_id == challenge_id).all()
    return [svc.get_group_detail("buddy", group.owner_id, group.id) for group in groups]


@router.post("/{challenge_id}/rewards", response_model=RewardOut, summary="Create a reward for this challenge")
def create_reward(challenge_id: uuid.UUID, payload: RewardCreate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    reward = ChallengeService(db).admin_create_reward(current_user.id, challenge_id, payload)
    return RewardOut(id=reward.id, challenge_id=reward.challenge_id, name=reward.name, description=reward.description, requirement_type=reward.requirement_type, requirement_value=reward.requirement_value, badge_icon=reward.badge_icon)


@router.get("/{challenge_id}/rewards", response_model=list[RewardOut], summary="List rewards for this challenge")
def list_rewards(challenge_id: uuid.UUID, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return ChallengeService(db).admin_list_rewards(challenge_id)


@router.delete("/rewards/{reward_id}", summary="Delete a reward")
def delete_reward(reward_id: uuid.UUID, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    ChallengeService(db).admin_delete_reward(current_user.id, reward_id)
    return {"success": True}
