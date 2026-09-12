"""Integration tests (real DB, rolled back per test) for pre-provisioning a
Church/Fellowship admin by email: they don't need an account yet at
creation time - the moment they sign up (or an admin creates their member
record) with that email, they become the org's owner automatically."""
import pytest

from app.core.exceptions import NotFoundError
from app.services.community_service import CommunityService
from app.repositories.user_repository import UserRepository
from app.schemas.community import ChurchCreate, FellowshipCreate


def test_admin_email_resolves_to_existing_user_immediately(db, make_user):
    creator = make_user()
    admin_to_be = make_user(email="pastor@example.com")
    community = CommunityService(db)

    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email="Pastor@Example.com"))

    assert church.owner_id == admin_to_be.id
    assert church.pending_admin_email is None
    detail = community.get_church_detail(admin_to_be.id, church.id)
    assert detail.my_role == "owner"


def test_admin_email_pre_provisions_before_signup_then_resolves_on_signup(db, make_user):
    creator = make_user()
    community = CommunityService(db)

    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email="future.pastor@example.com"))
    assert church.owner_id == creator.id  # placeholder until the real admin signs up
    assert church.pending_admin_email == "future.pastor@example.com"

    # not yet a member
    assert community._my_role("church", church.id, creator.id) == "owner"

    # the invited person signs up (simulated via UserService.create, which
    # funnels through the same UserRepository.create() bottleneck every
    # real signup path uses)
    new_admin = UserRepository(db).create_with_unique_id("Future", name="Future Pastor", email="future.pastor@example.com")

    db.refresh(church)
    assert church.owner_id == new_admin.id
    assert church.pending_admin_email is None
    assert community._my_role("church", church.id, new_admin.id) == "owner"


def test_admin_email_is_case_and_whitespace_insensitive(db, make_user):
    creator = make_user()
    community = CommunityService(db)
    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email="  Future.Admin@Example.com  "))
    assert church.pending_admin_email == "future.admin@example.com"

    new_admin = UserRepository(db).create_with_unique_id("Future", name="Future Admin", email="FUTURE.ADMIN@example.com")
    db.refresh(church)
    assert church.owner_id == new_admin.id


def test_fellowship_admin_email_pre_provisioning(db, make_user):
    creator = make_user()
    community = CommunityService(db)
    fellowship = community.admin_create_fellowship(creator.id, FellowshipCreate(name="Youth Fellowship", privacy="public", admin_email="future.leader@example.com"))
    assert fellowship.pending_admin_email == "future.leader@example.com"

    new_admin = UserRepository(db).create_with_unique_id("Future", name="Future Leader", email="future.leader@example.com")
    db.refresh(fellowship)
    assert fellowship.owner_id == new_admin.id
    assert community._my_role("fellowship", fellowship.id, new_admin.id) == "owner"


def test_invite_admin_by_email_requires_existing_account(db, make_user):
    owner = make_user()
    community = CommunityService(db)
    church = community.admin_create_church(owner.id, ChurchCreate(name="Grace Chapel", privacy="public"))

    with pytest.raises(NotFoundError):
        community.invite_admin_by_email(owner.id, "church", church.id, "nobody@example.com")


def test_invite_admin_by_email_adds_existing_user_as_admin_not_owner(db, make_user):
    owner = make_user()
    second_admin = make_user(email="second@example.com")
    community = CommunityService(db)
    church = community.admin_create_church(owner.id, ChurchCreate(name="Grace Chapel", privacy="public"))

    community.invite_admin_by_email(owner.id, "church", church.id, "second@example.com")

    detail = community.get_church_detail(second_admin.id, church.id)
    assert detail.my_role == "admin"
    # ownership was never reassigned by this path
    db.refresh(church)
    assert church.owner_id == owner.id


def test_pending_invite_resolves_at_login_even_if_the_account_was_created_outside_the_normal_signup_flow(db, make_user):
    """Regression test: a user account can come into existence through a
    path other than UserRepository.create() (e.g. CSV import builds a User
    row directly), which would leave a pending_admin_email unresolved
    forever if resolution only ran at account-creation time. AuthService
    now re-checks on every login, so this must resolve there instead."""
    from app.models.user import User, UserStatus
    from app.services.auth_service import AuthService

    creator = make_user()
    community = CommunityService(db)
    church = community.admin_create_church(creator.id, ChurchCreate(name="Grace Chapel", privacy="public", admin_email="bypassed.pastor@example.com"))
    assert church.pending_admin_email == "bypassed.pastor@example.com"

    # simulate a user created via a path that bypasses UserRepository.create()
    bypassed_user = User(user_id="BYPASS01", name="Bypassed Pastor", email="bypassed.pastor@example.com", status=UserStatus.active)
    db.add(bypassed_user)
    db.flush()
    db.commit()

    # still pending - creation never ran the resolution hook
    db.refresh(church)
    assert church.pending_admin_email == "bypassed.pastor@example.com"
    assert church.owner_id != bypassed_user.id

    response = AuthService(db).login(bypassed_user.user_id)

    db.refresh(church)
    assert church.pending_admin_email is None
    assert church.owner_id == bypassed_user.id
    assert len(response.admin_orgs) == 1
    assert response.admin_orgs[0].org_id == church.id
