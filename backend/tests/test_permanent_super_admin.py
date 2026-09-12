"""Integration tests (real DB, rolled back per test) for:
1. A configured permanent-super-admin email always being force-corrected
   to super_admin/active on every login, regardless of its current DB
   state (production is configured with admin.rootedbible@gmail.com; here
   we point the setting at a throwaway test email instead, since the real
   one is already seeded in the dev DB as ADMIN001).
2. A platform admin/super_admin always landing on the Super Admin
   Dashboard - even if they also happen to own/admin a Church or
   Fellowship - is a frontend routing concern, covered separately in
   completeSignIn.ts; here we only verify the backend never demotes or
   otherwise loses the permanent super admin's role."""
import pytest

from app.core.config import settings
from app.models.user import UserRole, UserStatus
from app.services.auth_service import AuthService
from app.services.community_service import CommunityService
from app.schemas.community import ChurchCreate

TEST_PERMANENT_EMAIL = "permanent.super.admin.test@example.com"


@pytest.fixture(autouse=True)
def _permanent_super_admin_email(monkeypatch):
    monkeypatch.setattr(settings, "PERMANENT_SUPER_ADMIN_EMAILS", [TEST_PERMANENT_EMAIL])


def test_permanent_super_admin_email_is_force_corrected_on_login(db, make_user):
    user = make_user(role="member", email=TEST_PERMANENT_EMAIL)
    assert user.role == UserRole.member

    response = AuthService(db).login(user.user_id)

    assert response.user.role == UserRole.super_admin
    db.refresh(user)
    assert user.role == UserRole.super_admin


def test_permanent_super_admin_is_reactivated_even_if_suspended(db, make_user):
    user = make_user(role="member", email=TEST_PERMANENT_EMAIL)
    user.status = UserStatus.suspended
    db.commit()

    response = AuthService(db).login(user.user_id)

    assert response.user.status == UserStatus.active


def test_permanent_super_admin_who_creates_a_church_is_never_tracked_as_its_admin(db, make_user):
    """The actual bug report (earlier architecture): this account creating
    a Church must never cost it its platform-wide role. Under the final
    architecture this is even stronger - assign_org_admin refuses to ever
    make a super_admin an org's ADMIN, so creating a church without
    assigning someone else leaves it with no tracked admin at all, and
    admin_orgs for this account stays empty."""
    user = make_user(role="member", email=TEST_PERMANENT_EMAIL)
    community = CommunityService(db)
    community.admin_create_church(user.id, ChurchCreate(name="Grace Chapel", privacy="public"))

    response = AuthService(db).login(user.user_id)

    assert response.user.role == UserRole.super_admin
    assert response.admin_orgs == []


def test_ordinary_users_are_not_affected(db, make_user):
    user = make_user(role="member", email="regular.member@example.com")
    response = AuthService(db).login(user.user_id)
    assert response.user.role == UserRole.member
