import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_admin
from app.core.exceptions import ValidationError
from app.models.user import User
from app.schemas.challenge import (
    RootedIdLookupOut, ChallengeSummaryOut, ChallengeDetailOut, ChallengeAdminOut,
    GroupCreate, GroupDetailOut, InviteByRootedId, JoinRequestOut, RewardEarnedOut, EncouragementCreate, EncouragementOut,
    LeaderboardConfigOut, LeaderboardOut,
)
from app.schemas.community import (
    ChurchCreate, ChurchOut, ChurchDetailOut, FellowshipCreate, FellowshipOut, FellowshipDetailOut,
    RootedGroupOut, MyGroupMembershipUpdate,
)
from app.services.challenge_service import ChallengeService
from app.services.community_service import CommunityService

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


@router.get("/challenges/{challenge_id}/leaderboards", response_model=list[LeaderboardConfigOut], summary="Available leaderboard scopes for this challenge")
def list_leaderboard_scopes(challenge_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChallengeService(db).admin_list_leaderboard_config(challenge_id)


@router.get("/challenges/{challenge_id}/leaderboards/{scope}", response_model=LeaderboardOut, summary="Ranked leaderboard for one scope (Family=Top1, others=Top3 by default)")
def get_leaderboard(challenge_id: uuid.UUID, scope: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChallengeService(db).get_leaderboard(challenge_id, scope)


@router.get("/requests", summary="My pending incoming and outgoing requests (challenge, family, buddy)")
def list_requests(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChallengeService(db).list_my_requests(current_user.id)


@router.post("/requests/{request_id}/cancel", summary="Cancel my own pending request")
def cancel_request(request_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ChallengeService(db).cancel_request(current_user.id, request_id)
    return {"success": True}


# -----------------------------------------------------------------------
# Family - standalone (no size cap); may optionally also be linked to a
# single Church Challenge for that challenge's leaderboard.
# -----------------------------------------------------------------------
@router.get("/family", response_model=list[GroupDetailOut], summary="Families I belong to")
def list_my_families(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChallengeService(db).list_my_groups("family", current_user.id)


@router.post("/family", response_model=GroupDetailOut, summary="Create your own Family (no member limit)")
def create_standalone_family(payload: GroupCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = ChallengeService(db)
    family = svc.create_group("family", current_user.id, payload)
    return svc.get_group_detail("family", current_user.id, family.id)


@router.post("/challenges/{challenge_id}/family", response_model=GroupDetailOut, summary="Create a Family that also participates in this Church Challenge")
def create_family(challenge_id: uuid.UUID, payload: GroupCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = ChallengeService(db)
    family = svc.create_group("family", current_user.id, payload, challenge_id=challenge_id)
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


@router.get("/family/{family_id}/encouragements", response_model=list[EncouragementOut], summary="Recent encouragements sent to this Family")
def list_family_encouragements(family_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChallengeService(db).list_group_encouragements("family", current_user.id, family_id)


# -----------------------------------------------------------------------
# Buddy Group - standalone (no size cap); may optionally also be linked to
# a single Church Challenge for that challenge's leaderboard.
# -----------------------------------------------------------------------
@router.get("/buddy-group", response_model=list[GroupDetailOut], summary="Buddy Groups I belong to")
def list_my_buddy_groups(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChallengeService(db).list_my_groups("buddy", current_user.id)


@router.post("/buddy-group", response_model=GroupDetailOut, summary="Create your own Buddy Group (no member limit)")
def create_standalone_buddy_group(payload: GroupCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = ChallengeService(db)
    group = svc.create_group("buddy", current_user.id, payload)
    return svc.get_group_detail("buddy", current_user.id, group.id)


@router.post("/challenges/{challenge_id}/buddy-group", response_model=GroupDetailOut, summary="Create a Buddy Group that also participates in this Church Challenge")
def create_buddy_group(challenge_id: uuid.UUID, payload: GroupCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = ChallengeService(db)
    group = svc.create_group("buddy", current_user.id, payload, challenge_id=challenge_id)
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


@router.get("/buddy-group/{group_id}/encouragements", response_model=list[EncouragementOut], summary="Recent encouragements sent to this Buddy Group")
def list_buddy_group_encouragements(group_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChallengeService(db).list_group_encouragements("buddy", current_user.id, group_id)


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


# -----------------------------------------------------------------------
# Church - standalone, discoverable via church_code
# -----------------------------------------------------------------------
@router.get("/church", response_model=list[ChurchOut], summary="Churches I belong to")
def list_my_churches(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return CommunityService(db).list_my_churches(current_user.id)


@router.post("/church", response_model=ChurchOut, summary="Create a Church (admin only)")
def create_church(payload: ChurchCreate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = CommunityService(db)
    church = svc.admin_create_church(current_user.id, payload)
    return svc._to_church_out(church, current_user.id)


@router.get("/church/discover", response_model=list[ChurchOut], summary="Public churches I can request to join")
def discover_churches(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return CommunityService(db).list_discoverable_churches(current_user.id)


@router.get("/church/{church_id}", response_model=ChurchDetailOut, summary="Church detail")
def get_church(church_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return CommunityService(db).get_church_detail(current_user.id, church_id)


@router.post("/church/{church_id}/join", summary="Request to join a Church")
def join_church(church_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    request = CommunityService(db).request_join_church(current_user.id, church_id=church_id)
    return {"request_id": request.id, "status": request.status}


@router.post("/church/join-by-code/{church_code}", summary="Request to join a Church by its code")
def join_church_by_code(church_code: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    request = CommunityService(db).request_join_church(current_user.id, church_code=church_code)
    return {"request_id": request.id, "status": request.status}


@router.get("/church/{church_id}/requests", summary="Pending join requests for this church (admin only)")
def list_church_requests(church_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return CommunityService(db).list_pending_church_requests(current_user.id, church_id)


@router.post("/church/requests/{request_id}/approve", summary="Approve a church join request (admin only)")
def approve_church_request(request_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    CommunityService(db).respond_to_church_request(current_user.id, request_id, approve=True)
    return {"success": True}


@router.post("/church/requests/{request_id}/decline", summary="Decline a church join request (admin only)")
def decline_church_request(request_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    CommunityService(db).respond_to_church_request(current_user.id, request_id, approve=False)
    return {"success": True}


@router.post("/church/{church_id}/leave", summary="Leave this Church")
def leave_church(church_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    CommunityService(db).leave_church(current_user.id, church_id)
    return {"success": True}


@router.delete("/church/{church_id}/members/{rooted_id}", summary="Remove a member (admin only)")
def remove_church_member(church_id: uuid.UUID, rooted_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    CommunityService(db).remove_church_member(current_user.id, church_id, rooted_id)
    return {"success": True}


# -----------------------------------------------------------------------
# Fellowship - standalone, optionally scoped to a Church
# -----------------------------------------------------------------------
@router.get("/fellowship", response_model=list[FellowshipOut], summary="Fellowships I belong to")
def list_my_fellowships(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return CommunityService(db).list_my_fellowships(current_user.id)


@router.post("/fellowship", response_model=FellowshipOut, summary="Create a Fellowship (admin only)")
def create_fellowship(payload: FellowshipCreate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = CommunityService(db)
    fellowship = svc.admin_create_fellowship(current_user.id, payload)
    return svc._to_fellowship_out(fellowship, current_user.id)


@router.get("/fellowship/discover", response_model=list[FellowshipOut], summary="Public fellowships I can request to join")
def discover_fellowships(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return CommunityService(db).list_discoverable_fellowships(current_user.id)


@router.get("/fellowship/{fellowship_id}", response_model=FellowshipDetailOut, summary="Fellowship detail")
def get_fellowship(fellowship_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return CommunityService(db).get_fellowship_detail(current_user.id, fellowship_id)


@router.post("/fellowship/{fellowship_id}/join", summary="Request to join a Fellowship")
def join_fellowship(fellowship_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    request = CommunityService(db).request_join_fellowship(current_user.id, fellowship_id=fellowship_id)
    return {"request_id": request.id, "status": request.status}


@router.post("/fellowship/join-by-code/{fellowship_code}", summary="Request to join a Fellowship by its code")
def join_fellowship_by_code(fellowship_code: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    request = CommunityService(db).request_join_fellowship(current_user.id, fellowship_code=fellowship_code)
    return {"request_id": request.id, "status": request.status}


@router.get("/fellowship/{fellowship_id}/requests", summary="Pending join requests for this fellowship (admin only)")
def list_fellowship_requests(fellowship_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return CommunityService(db).list_pending_fellowship_requests(current_user.id, fellowship_id)


@router.post("/fellowship/requests/{request_id}/approve", summary="Approve a fellowship join request (admin only)")
def approve_fellowship_request(request_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    CommunityService(db).respond_to_fellowship_request(current_user.id, request_id, approve=True)
    return {"success": True}


@router.post("/fellowship/requests/{request_id}/decline", summary="Decline a fellowship join request (admin only)")
def decline_fellowship_request(request_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    CommunityService(db).respond_to_fellowship_request(current_user.id, request_id, approve=False)
    return {"success": True}


@router.post("/fellowship/{fellowship_id}/leave", summary="Leave this Fellowship")
def leave_fellowship(fellowship_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    CommunityService(db).leave_fellowship(current_user.id, fellowship_id)
    return {"success": True}


@router.delete("/fellowship/{fellowship_id}/members/{rooted_id}", summary="Remove a member (admin only)")
def remove_fellowship_member(fellowship_id: uuid.UUID, rooted_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    CommunityService(db).remove_fellowship_member(current_user.id, fellowship_id, rooted_id)
    return {"success": True}


# -----------------------------------------------------------------------
# Rooted Group (Sunday / Blazer / Youth / Men / Women)
# -----------------------------------------------------------------------
@router.get("/groups", response_model=list[RootedGroupOut], summary="All active Rooted groups")
def list_groups(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return CommunityService(db).list_groups()


@router.get("/groups/mine", response_model=list[str], summary="Group IDs I belong to")
def my_groups(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [str(g) for g in CommunityService(db).get_my_group_ids(current_user.id)]


@router.put("/groups/mine", summary="Set my group memberships (replaces the full set)")
def set_my_groups(payload: MyGroupMembershipUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    CommunityService(db).set_my_groups(current_user.id, payload.group_ids)
    return {"success": True}
