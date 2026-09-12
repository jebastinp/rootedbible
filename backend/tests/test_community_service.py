"""Integration tests (real DB, rolled back per test) for the standalone
Family/Buddy Group business rule - no owning Church Challenge is required,
and there is no member cap anywhere in the create/join path."""
import pytest

from app.core.exceptions import ForbiddenError
from app.services.challenge_service import ChallengeService
from app.services.community_service import CommunityService
from app.schemas.challenge import GroupCreate
from app.schemas.community import ChurchCreate, FellowshipCreate


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
    super_admin = make_user(role="super_admin")
    owner = make_user()
    joiner = make_user()
    service = CommunityService(db)

    church = service.admin_create_church(super_admin.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email=owner.email))
    assert church.church_code.startswith("ROOTED-")

    request = service.request_join_church(joiner.id, church_code=church.church_code)
    assert request.status == "pending"

    service.respond_to_church_request(owner.id, request.id, approve=True)

    detail = service.get_church_detail(owner.id, church.id)
    assert detail.member_count == 2
    member_ids = {m.user_id for m in detail.members}
    assert joiner.user_id in member_ids


def test_fellowship_join_by_code_then_approve(db, make_user):
    super_admin = make_user(role="super_admin")
    owner = make_user()
    joiner = make_user()
    service = CommunityService(db)

    fellowship = service.admin_create_fellowship(super_admin.id, FellowshipCreate(name="Youth Fellowship", privacy="public", admin_email=owner.email))
    assert fellowship.fellowship_code.startswith("ROOTED-")

    request = service.request_join_fellowship(joiner.id, fellowship_code=fellowship.fellowship_code)
    assert request.status == "pending"

    service.respond_to_fellowship_request(owner.id, request.id, approve=True)

    detail = service.get_fellowship_detail(owner.id, fellowship.id)
    assert detail.member_count == 2
    member_ids = {m.user_id for m in detail.members}
    assert joiner.user_id in member_ids


def test_fellowship_join_by_code_is_case_insensitive_and_unknown_code_rejected(db, make_user):
    super_admin = make_user(role="super_admin")
    joiner = make_user()
    service = CommunityService(db)
    fellowship = service.admin_create_fellowship(super_admin.id, FellowshipCreate(name="Men's Fellowship", privacy="public"))

    request = service.request_join_fellowship(joiner.id, fellowship_code=fellowship.fellowship_code.lower())
    assert request.fellowship_id == fellowship.id

    from app.core.exceptions import NotFoundError
    other = make_user()
    with pytest.raises(NotFoundError):
        service.request_join_fellowship(other.id, fellowship_code="ROOTED-NOPE00")


def test_private_church_still_visible_to_platform_admin(db, make_user):
    """Rule 6: Super Admin must see every Family/Buddy/Church/Fellowship,
    including private ones, in the platform-wide admin listing."""
    super_admin = make_user(role="super_admin")
    service = CommunityService(db)
    church = service.admin_create_church(super_admin.id, ChurchCreate(name="Private Fellowship House", privacy="private"))

    all_churches = service.admin_list_all_churches()
    ids = {c.id for c in all_churches}
    assert church.id in ids

    # and it must NOT show up in the public discover feed for someone else
    outsider = make_user()
    discoverable = service.list_discoverable_churches(outsider.id)
    assert church.id not in {c.id for c in discoverable}


def test_cannot_join_church_twice(db, make_user):
    super_admin = make_user(role="super_admin")
    owner = make_user()
    joiner = make_user()
    service = CommunityService(db)
    church = service.admin_create_church(super_admin.id, ChurchCreate(name="Second Request Church", privacy="public", admin_email=owner.email))
    request = service.request_join_church(joiner.id, church_id=church.id)
    service.respond_to_church_request(owner.id, request.id, approve=True)

    with pytest.raises(Exception):
        service.request_join_church(joiner.id, church_id=church.id)


# -----------------------------------------------------------------------
# Cross-organization isolation (final architecture): an `admin` is scoped
# to EXACTLY one organization via AdminOrganizationAssignment - never via
# the global User.role field alone. These tests prove Church A's admin
# cannot read or act on Church B's data by any of the vectors called out
# (viewing, approving requests, viewing members), i.e. an IDOR probe
# against the service layer directly (the same layer the API routes call
# with no additional gate in between).
# -----------------------------------------------------------------------
def test_church_admin_cannot_view_another_churchs_pending_requests(db, make_user):
    super_admin = make_user(role="super_admin")
    admin_a = make_user()
    admin_b = make_user()
    joiner = make_user()
    service = CommunityService(db)

    church_a = service.admin_create_church(super_admin.id, ChurchCreate(name="Church A", privacy="public", admin_email=admin_a.email))
    church_b = service.admin_create_church(super_admin.id, ChurchCreate(name="Church B", privacy="public", admin_email=admin_b.email))
    service.request_join_church(joiner.id, church_id=church_b.id)

    with pytest.raises(ForbiddenError):
        service.list_pending_church_requests(admin_a.id, church_b.id)

    # sanity: Church B's own admin CAN see it
    assert len(service.list_pending_church_requests(admin_b.id, church_b.id)) == 1
    del church_a  # only needed to exist as the "other" organization


def test_church_admin_cannot_approve_another_churchs_request(db, make_user):
    super_admin = make_user(role="super_admin")
    admin_a = make_user()
    admin_b = make_user()
    joiner = make_user()
    service = CommunityService(db)

    service.admin_create_church(super_admin.id, ChurchCreate(name="Church A", privacy="public", admin_email=admin_a.email))
    church_b = service.admin_create_church(super_admin.id, ChurchCreate(name="Church B", privacy="public", admin_email=admin_b.email))
    request = service.request_join_church(joiner.id, church_id=church_b.id)

    with pytest.raises(ForbiddenError):
        service.respond_to_church_request(admin_a.id, request.id, approve=True)

    # request must still be pending - the denied attempt must not have side effects
    still_pending = service.list_pending_church_requests(admin_b.id, church_b.id)
    assert len(still_pending) == 1


def test_church_admin_cannot_view_another_churchs_members(db, make_user):
    super_admin = make_user(role="super_admin")
    admin_a = make_user()
    admin_b = make_user()
    service = CommunityService(db)

    service.admin_create_church(super_admin.id, ChurchCreate(name="Church A", privacy="public", admin_email=admin_a.email))
    church_b = service.admin_create_church(super_admin.id, ChurchCreate(name="Church B", privacy="public", admin_email=admin_b.email))

    # get_church_detail doesn't raise for a non-member - it just omits the
    # members list entirely, which is the correct "no access" behavior
    detail = service.get_church_detail(admin_a.id, church_b.id)
    assert detail.members == []
    assert detail.my_role is None


def test_fellowship_admin_cannot_view_or_approve_another_fellowships_requests(db, make_user):
    super_admin = make_user(role="super_admin")
    admin_a = make_user()
    admin_b = make_user()
    joiner = make_user()
    service = CommunityService(db)

    service.admin_create_fellowship(super_admin.id, FellowshipCreate(name="Fellowship A", privacy="public", admin_email=admin_a.email))
    fellowship_b = service.admin_create_fellowship(super_admin.id, FellowshipCreate(name="Fellowship B", privacy="public", admin_email=admin_b.email))
    request = service.request_join_fellowship(joiner.id, fellowship_id=fellowship_b.id)

    with pytest.raises(ForbiddenError):
        service.list_pending_fellowship_requests(admin_a.id, fellowship_b.id)

    with pytest.raises(ForbiddenError):
        service.respond_to_fellowship_request(admin_a.id, request.id, approve=True)

    # Fellowship B's own admin can still act on it correctly
    service.respond_to_fellowship_request(admin_b.id, request.id, approve=True)
    detail = service.get_fellowship_detail(admin_b.id, fellowship_b.id)
    assert detail.member_count == 2


def test_admin_role_alone_grants_no_church_access(db, make_user):
    """The critical distinction: User.role == 'admin' means nothing on its
    own - it must be paired with a matching AdminOrganizationAssignment.
    A different `admin` (managing a DIFFERENT, or no, organization) must
    never gain access just by sharing the role name."""
    super_admin = make_user(role="super_admin")
    creator_admin = make_user()
    other_admin = make_user(role="admin")  # role=admin but no assignment at all
    service = CommunityService(db)

    church = service.admin_create_church(super_admin.id, ChurchCreate(name="Isolated Church", privacy="public", admin_email=creator_admin.email))

    with pytest.raises(ForbiddenError):
        service.list_pending_church_requests(other_admin.id, church.id)


def test_church_creation_assigns_a_specific_admin_by_rooted_id(db, make_user):
    """Spec sections 5-6: creating a Church/Fellowship should support
    assigning a DIFFERENT person as its scoped admin, not always default
    to whoever is filling out the creation form."""
    super_admin = make_user(role="super_admin")
    pastor = make_user()
    service = CommunityService(db)

    church = service.admin_create_church(
        super_admin.id,
        ChurchCreate(name="St. John's Church", privacy="public", admin_rooted_id=pastor.user_id),
    )

    # the assigned pastor is the owner - the super_admin who filled the
    # form is NOT automatically a member of this specific church
    detail = service.get_church_detail(pastor.id, church.id)
    assert detail.my_role == "owner"
    assert detail.member_count == 1

    unrelated_member = service.get_church_detail(pastor.id, church.id).members[0]
    assert unrelated_member.user_id == pastor.user_id


def test_super_admin_can_override_and_manage_any_church(db, make_user):
    """Spec: 'Super Admin can access all organizations' - unlike a plain
    admin, super_admin must be able to act on a church it never joined
    (approve requests, etc.), not just view it read-only."""
    super_admin = make_user(role="super_admin")
    church_owner = make_user()
    joiner = make_user()
    service = CommunityService(db)

    church = service.admin_create_church(super_admin.id, ChurchCreate(name="Church With Override", privacy="public", admin_email=church_owner.email))
    request = service.request_join_church(joiner.id, church_id=church.id)

    # super_admin never joined this church, but must still be able to act
    pending = service.list_pending_church_requests(super_admin.id, church.id)
    assert len(pending) == 1

    service.respond_to_church_request(super_admin.id, request.id, approve=True)
    detail = service.get_church_detail(church_owner.id, church.id)
    assert detail.member_count == 2
