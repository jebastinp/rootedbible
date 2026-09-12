"""Integration tests (real DB, rolled back per test) for assigning a
Church/Fellowship's ADMIN by email or Rooted ID - the final architecture
has NO "pending invite" state: the target must already be an existing
Rooted member, or the call fails immediately and clearly. See
CommunityService.assign_org_admin."""
import pytest

from app.core.exceptions import NotFoundError, ValidationError, ConflictError
from app.services.community_service import CommunityService
from app.schemas.community import ChurchCreate, FellowshipCreate


def test_admin_email_resolves_to_existing_member_at_creation(db, make_user):
    creator = make_user(role="super_admin")
    pastor = make_user(email="pastor@example.com")
    community = CommunityService(db)

    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email="Pastor@Example.com"))

    detail = community.get_church_detail(pastor.id, church.id)
    assert detail.my_role == "owner"
    assert detail.admin.user_id == pastor.user_id
    db.refresh(pastor)
    assert pastor.role.value == "admin"


def test_admin_email_that_does_not_exist_fails_immediately_with_no_pending_state(db, make_user):
    """The core behavior change: no more silent 'pending' placeholder -
    an unresolvable email fails the call right away."""
    creator = make_user(role="super_admin")
    community = CommunityService(db)

    with pytest.raises(NotFoundError):
        community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email="nobody.registered@example.com"))


def test_admin_email_is_case_and_whitespace_insensitive(db, make_user):
    creator = make_user(role="super_admin")
    pastor = make_user(email="future.admin@example.com")
    community = CommunityService(db)

    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email="  Future.Admin@Example.com  "))

    db.refresh(pastor)
    assert pastor.role.value == "admin"
    assert community._is_org_admin("church", church.id, pastor.id)


def test_fellowship_admin_email_assignment(db, make_user):
    creator = make_user(role="super_admin")
    leader = make_user(email="leader@example.com")
    community = CommunityService(db)

    fellowship = community.admin_create_fellowship(creator.id, FellowshipCreate(name="Youth Fellowship", privacy="public", admin_email="leader@example.com"))

    db.refresh(leader)
    assert leader.role.value == "admin"
    assert community._is_org_admin("fellowship", fellowship.id, leader.id)


def test_super_admin_cannot_be_assigned_as_an_org_admin(db, make_user):
    creator = make_user(role="super_admin")
    other_super_admin = make_user(role="super_admin", email="other.super@example.com")
    community = CommunityService(db)

    with pytest.raises(ValidationError):
        community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email="other.super@example.com"))


def test_assigning_someone_who_already_admins_another_org_is_rejected_without_reassign(db, make_user):
    creator = make_user(role="super_admin")
    busy_admin = make_user(email="busy@example.com")
    community = CommunityService(db)
    community.admin_create_church(creator.id, ChurchCreate(name="Church A", privacy="public", admin_email="busy@example.com"))

    with pytest.raises(ConflictError):
        community.admin_create_church(creator.id, ChurchCreate(name="Church B", privacy="public", admin_email="busy@example.com"))


def test_reassigning_an_existing_admin_moves_them_to_the_new_org(db, make_user):
    creator = make_user(role="super_admin")
    admin_user = make_user(email="mover@example.com")
    community = CommunityService(db)
    church_a = community.admin_create_church(creator.id, ChurchCreate(name="Church A", privacy="public", admin_email="mover@example.com"))
    church_b = community.admin_create_church(creator.id, ChurchCreate(name="Church B", privacy="public"))

    community.assign_org_admin(creator.id, "church", church_b.id, admin_email="mover@example.com", reassign=True)

    assert not community._is_org_admin("church", church_a.id, admin_user.id)
    assert community._is_org_admin("church", church_b.id, admin_user.id)


def test_reassigning_an_org_to_a_new_admin_demotes_the_previous_one_to_member(db, make_user):
    creator = make_user(role="super_admin")
    first_admin = make_user(email="first@example.com")
    second_admin = make_user(email="second@example.com")
    community = CommunityService(db)
    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email="first@example.com"))

    community.assign_org_admin(creator.id, "church", church.id, admin_email="second@example.com", reassign=True)

    db.refresh(first_admin)
    assert first_admin.role.value == "member"
    assert not community._is_org_admin("church", church.id, first_admin.id)
    assert community._is_org_admin("church", church.id, second_admin.id)
