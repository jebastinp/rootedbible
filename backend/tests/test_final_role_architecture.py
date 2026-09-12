"""Integration tests (real DB, rolled back per test) for the final 3-role
architecture's hard invariants:
1. AdminOrganizationAssignment's DB-level uniqueness constraints (one
   admin per user, one admin per org) hold even if application code ever
   forgets to check - this is a last line of defense, not the primary gate.
2. An `admin` (org-scoped) is rejected by every platform-wide-only
   endpoint at the API layer, not just in the service layer.
3. UserRole has exactly 3 values - `leader` no longer exists."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.main import app
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import UserRole
from app.models.admin_assignment import AdminOrganizationAssignment
from app.services.community_service import CommunityService
from app.schemas.community import ChurchCreate, FellowshipCreate


def test_user_role_has_exactly_three_values():
    assert {r.value for r in UserRole} == {"member", "admin", "super_admin"}


@pytest.fixture()
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        app.dependency_overrides[get_current_user] = lambda: c.current_user
        yield c
    app.dependency_overrides.clear()


def _as(client, user):
    client.current_user = user


def test_db_rejects_a_second_admin_organization_assignment_for_the_same_user(db, make_user):
    """Last line of defense: even bypassing assign_org_admin entirely, the
    database itself refuses to let one user manage two organizations."""
    admin_user = make_user(role="admin")
    community = CommunityService(db)
    church_a = community.admin_create_church(make_user(role="super_admin").id, ChurchCreate(name="Church A", privacy="public"))
    church_b = community.admin_create_church(make_user(role="super_admin").id, ChurchCreate(name="Church B", privacy="public"))

    db.add(AdminOrganizationAssignment(user_id=admin_user.id, organization_type="church", church_id=church_a.id))
    db.flush()
    db.add(AdminOrganizationAssignment(user_id=admin_user.id, organization_type="church", church_id=church_b.id))
    with pytest.raises(IntegrityError):
        db.flush()


def test_db_rejects_two_admins_for_the_same_church(db, make_user):
    admin_1 = make_user(role="admin")
    admin_2 = make_user(role="admin")
    community = CommunityService(db)
    church = community.admin_create_church(make_user(role="super_admin").id, ChurchCreate(name="Church A", privacy="public"))

    db.add(AdminOrganizationAssignment(user_id=admin_1.id, organization_type="church", church_id=church.id))
    db.flush()
    db.add(AdminOrganizationAssignment(user_id=admin_2.id, organization_type="church", church_id=church.id))
    with pytest.raises(IntegrityError):
        db.flush()


@pytest.mark.parametrize("method,path", [
    ("get", "/api/v1/admin/churches"),
    ("get", "/api/v1/admin/fellowships"),
    ("get", "/api/v1/admin/members"),
    ("get", "/api/v1/admin/reading-plan"),
    ("get", "/api/v1/admin/reports/members"),
    ("get", "/api/v1/admin/csv-import/history"),
    ("get", "/api/v1/admin/audit-logs"),
])
def test_org_admin_is_rejected_by_every_platform_only_endpoint(client, make_user, method, path):
    """An `admin` must never reach ANY platform-wide capability - only
    Super Admin can. Covers the full surface that used to accept both
    admin+super_admin before the final architecture."""
    org_admin = make_user(role="admin")
    _as(client, org_admin)
    resp = getattr(client, method)(path)
    assert resp.status_code == 403


@pytest.mark.parametrize("method,path", [
    ("get", "/api/v1/admin/churches"),
    ("get", "/api/v1/admin/fellowships"),
    ("get", "/api/v1/admin/members"),
])
def test_super_admin_can_reach_platform_only_endpoints(client, make_user, method, path):
    super_admin = make_user(role="super_admin")
    _as(client, super_admin)
    resp = getattr(client, method)(path)
    assert resp.status_code == 200


def test_org_admin_cannot_reach_another_orgs_reading_plan_via_api(client, db, make_user):
    """URL/API manipulation test (spec sections 13-14): even swapping the
    org_id in the URL must be rejected server-side, never trusted from
    the frontend."""
    super_admin = make_user(role="super_admin")
    admin_a = make_user()
    community = CommunityService(db)
    church_a = community.admin_create_church(super_admin.id, ChurchCreate(name="Church A", privacy="public", admin_email=admin_a.email))
    church_b = community.admin_create_church(super_admin.id, ChurchCreate(name="Church B", privacy="public"))

    db.refresh(admin_a)
    _as(client, admin_a)
    resp = client.get(f"/api/v1/community/church/{church_b.id}/reading-plan")
    assert resp.status_code == 403

    # sanity: admin_a CAN reach their own church's reading plan
    resp_own = client.get(f"/api/v1/community/church/{church_a.id}/reading-plan")
    assert resp_own.status_code == 200
