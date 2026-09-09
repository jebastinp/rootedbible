import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.core.exceptions import ValidationError
from app.models.user import User
from app.schemas.challenge import (
    RootedIdLookupOut, ChallengeSummaryOut, ChallengeDetailOut, ChallengeAdminOut,
    GroupCreate, GroupDetailOut, InviteByRootedId, JoinRequestOut, RewardEarnedOut, EncouragementCreate,
)
from app.services.challenge_service import ChallengeService

router = APIRouter(prefix="/community", tags=["Community"])


@router.get("/lookup/{rooted_id}", response_model=RootedIdLookupOut, summary="Identify a person by Rooted ID before inviting them")
def lookup_rooted_id(rooted_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChallengeService(db).lookup_rooted_id(rooted_id)


@router.get("/challenges", response_model=list[ChallengeSummaryOut], summary="My Church Challenges")
def list_my_challenges(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChallengeService(db).list_my_challenges(current_user.id)


@router.get("/challenges/discover", response_model=list[ChallengeAdminOut], summary="Church Challenges I can request to join")
def discover_challenges(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChallengeService(db).list_joinable_challenges(current_user.id)


@router.post("/challenges/{challenge_id}/join", summary="Request to join a Church Challenge")
def join_challenge(challenge_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    request = ChallengeService(db).request_join_challenge(current_user.id, challenge_id)
    return {"request_id": request.id, "status": request.status}


@router.get("/challenges/{challenge_id}", response_model=ChallengeDetailOut, summary="Church Challenge dashboard")
def get_challenge_detail(challenge_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChallengeService(db).get_challenge_detail(current_user.id, challenge_id)


@router.get("/challenges/{challenge_id}/rewards", response_model=list[RewardEarnedOut], summary="My rewards for this challenge")
def my_rewards(challenge_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChallengeService(db).list_my_rewards(current_user.id, challenge_id)


@router.get("/requests", summary="My pending incoming and outgoing requests (challenge, family, buddy)")
def list_requests(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChallengeService(db).list_my_requests(current_user.id)


@router.post("/requests/{request_id}/cancel", summary="Cancel my own pending request")
def cancel_request(request_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ChallengeService(db).cancel_request(current_user.id, request_id)
    return {"success": True}


# -----------------------------------------------------------------------
# Family - always scoped to a Church Challenge
# -----------------------------------------------------------------------
@router.post("/challenges/{challenge_id}/family", response_model=GroupDetailOut, summary="Create a Family inside this Church Challenge")
def create_family(challenge_id: uuid.UUID, payload: GroupCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = ChallengeService(db)
    family = svc.create_group("family", current_user.id, challenge_id, payload)
    return svc.get_group_detail("family", current_user.id, family.id)


@router.get("/family/{family_id}", response_model=GroupDetailOut, summary="Family detail")
def get_family(family_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChallengeService(db).get_group_detail("family", current_user.id, family_id)


@router.post("/family/{family_id}/invite", summary="Invite a fellow challenge participant to this Family by Rooted ID")
def invite_to_family(family_id: uuid.UUID, payload: InviteByRootedId, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    request = ChallengeService(db).invite_to_group("family", current_user.id, family_id, payload.rooted_id)
    return {"request_id": request.id, "status": request.status}


@router.post("/family/{family_id}/leave", summary="Leave this Family")
def leave_family(family_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ChallengeService(db).leave_group("family", current_user.id, family_id)
    return {"success": True}


@router.delete("/family/{family_id}/members/{rooted_id}", summary="Remove a member (owner only)")
def remove_family_member(family_id: uuid.UUID, rooted_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ChallengeService(db).remove_group_member("family", current_user.id, family_id, rooted_id)
    return {"success": True}


@router.delete("/family/{family_id}", summary="Delete this Family (owner only)")
def delete_family(family_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ChallengeService(db).delete_group("family", current_user.id, family_id)
    return {"success": True}


@router.post("/family/{family_id}/encourage", summary="Send a Family a predefined encouragement message")
def encourage_family(family_id: uuid.UUID, payload: EncouragementCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ChallengeService(db).send_group_encouragement("family", current_user.id, family_id, payload)
    return {"success": True}


# -----------------------------------------------------------------------
# Buddy Group - always scoped to a Church Challenge
# -----------------------------------------------------------------------
@router.post("/challenges/{challenge_id}/buddy-group", response_model=GroupDetailOut, summary="Create a Buddy Group inside this Church Challenge")
def create_buddy_group(challenge_id: uuid.UUID, payload: GroupCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = ChallengeService(db)
    group = svc.create_group("buddy", current_user.id, challenge_id, payload)
    return svc.get_group_detail("buddy", current_user.id, group.id)


@router.get("/buddy-group/{group_id}", response_model=GroupDetailOut, summary="Buddy Group detail")
def get_buddy_group(group_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChallengeService(db).get_group_detail("buddy", current_user.id, group_id)


@router.post("/buddy-group/{group_id}/invite", summary="Invite a fellow challenge participant to this Buddy Group by Rooted ID")
def invite_to_buddy_group(group_id: uuid.UUID, payload: InviteByRootedId, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    request = ChallengeService(db).invite_to_group("buddy", current_user.id, group_id, payload.rooted_id)
    return {"request_id": request.id, "status": request.status}


@router.post("/buddy-group/{group_id}/leave", summary="Leave this Buddy Group")
def leave_buddy_group(group_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ChallengeService(db).leave_group("buddy", current_user.id, group_id)
    return {"success": True}


@router.delete("/buddy-group/{group_id}/members/{rooted_id}", summary="Remove a member (owner only)")
def remove_buddy_member(group_id: uuid.UUID, rooted_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ChallengeService(db).remove_group_member("buddy", current_user.id, group_id, rooted_id)
    return {"success": True}


@router.delete("/buddy-group/{group_id}", summary="Delete this Buddy Group (owner only)")
def delete_buddy_group(group_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ChallengeService(db).delete_group("buddy", current_user.id, group_id)
    return {"success": True}


@router.post("/buddy-group/{group_id}/encourage", summary="Encourage the Buddy Group, or one member, with a predefined message")
def encourage_buddy_group(group_id: uuid.UUID, payload: EncouragementCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ChallengeService(db).send_group_encouragement("buddy", current_user.id, group_id, payload)
    return {"success": True}


# -----------------------------------------------------------------------
# Requests targeted at a Family/Buddy invite land here (accept/decline) -
# both kinds share the same JoinRequest table, so responding needs to know
# which service method to call based on the request's `type`.
# -----------------------------------------------------------------------
def _respond_to_family_or_buddy_request(db: Session, current_user: User, request_id: uuid.UUID, accept: bool) -> None:
    svc = ChallengeService(db)
    request = svc._get_request(request_id)
    if request.type not in ("family", "buddy"):
        raise ValidationError("Church Challenge join requests are approved by a Rooted admin, not here.")
    svc.respond_to_group_request(request.type, current_user.id, request_id, accept=accept)


@router.post("/requests/{request_id}/accept", summary="Accept a Family or Buddy Group invitation")
def accept_group_request(request_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _respond_to_family_or_buddy_request(db, current_user, request_id, accept=True)
    return {"success": True}


@router.post("/requests/{request_id}/decline", summary="Decline a Family or Buddy Group invitation")
def decline_group_request(request_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _respond_to_family_or_buddy_request(db, current_user, request_id, accept=False)
    return {"success": True}
