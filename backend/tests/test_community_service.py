"""Integration tests (real DB, rolled back per test) for the standalone
Family/Buddy Group business rule - no owning Church Challenge is required,
and there is no member cap anywhere in the create/join path."""
import pytest

from app.services.challenge_service import ChallengeService
from app.services.community_service import CommunityService
from app.schemas.challenge import GroupCreate
from app.schemas.community import ChurchCreate


@pytest.mark.parametrize("kind", ["family", "buddy"])
def test_create_standalone_group_without_challenge(db, make_user, kind):
    owner = make_user()
    service = ChallengeService(db)

    group = service.create_group(kind, owner.id, GroupCreate(name="My Circle"), challenge_id=None)

    assert group.challenge_id is None
    assert group.name == "My Circle"

    detail = service.get_group_detail(kind, owner.id, group.id)
    assert detail.max_members is None
    assert len(detail.members) == 1
    assert detail.members[0].role == "owner"


@pytest.mark.parametrize("kind", ["family", "buddy"])
def test_standalone_group_has_no_member_cap(db, make_user, kind):
    """The whole point of Rule 2-6: create as many members as you want,
    there is no artificial ceiling anywhere in the invite/accept path."""
    owner = make_user()
    service = ChallengeService(db)
    group = service.create_group(kind, owner.id, GroupCreate(name="Big Circle"), challenge_id=None)

    members = [owner]
    for _ in range(12):  # comfortably more than the old hardcoded 4/8-style caps
        invitee = make_user()
        request = service.invite_to_group(kind, owner.id, group.id, invitee.user_id)
        service.respond_to_group_request(kind, invitee.id, request.id, accept=True)
        members.append(invitee)

    detail = service.get_group_detail(kind, owner.id, group.id)
    assert detail.max_members is None
    assert len(detail.members) == 13


def test_group_create_does_not_require_challenge_participation(db, make_user):
    """Standalone family/buddy creation must not require any active
    Church Challenge membership - that constraint only applies when a
    challenge_id is explicitly passed in."""
    owner = make_user()
    service = ChallengeService(db)
    # owner has never joined any challenge - this must still succeed
    group = service.create_group("family", owner.id, GroupCreate(name="No Challenge Needed"), challenge_id=None)
    assert group.id is not None


def test_church_join_by_code_then_approve(db, make_user):
    owner = make_user()
    joiner = make_user()
    service = CommunityService(db)

    church = service.admin_create_church(owner.id, ChurchCreate(name="Grace Chapel", privacy="public"))
    assert church.church_code.startswith("ROOTED-")

    request = service.request_join_church(joiner.id, church_code=church.church_code)
    assert request.status == "pending"

    service.respond_to_church_request(owner.id, request.id, approve=True)

    detail = service.get_church_detail(owner.id, church.id)
    assert detail.member_count == 2
    member_ids = {m.user_id for m in detail.members}
    assert joiner.user_id in member_ids


def test_private_church_still_visible_to_platform_admin(db, make_user):
    """Rule 6: Super Admin must see every Family/Buddy/Church/Fellowship,
    including private ones, in the platform-wide admin listing."""
    owner = make_user()
    service = CommunityService(db)
    church = service.admin_create_church(owner.id, ChurchCreate(name="Private Fellowship House", privacy="private"))

    all_churches = service.admin_list_all_churches()
    ids = {c.id for c in all_churches}
    assert church.id in ids

    # and it must NOT show up in the public discover feed for someone else
    outsider = make_user()
    discoverable = service.list_discoverable_churches(outsider.id)
    assert church.id not in {c.id for c in discoverable}


def test_cannot_join_church_twice(db, make_user):
    owner = make_user()
    joiner = make_user()
    service = CommunityService(db)
    church = service.admin_create_church(owner.id, ChurchCreate(name="Second Request Church", privacy="public"))
    request = service.request_join_church(joiner.id, church_id=church.id)
    service.respond_to_church_request(owner.id, request.id, approve=True)

    with pytest.raises(Exception):
        service.request_join_church(joiner.id, church_id=church.id)
