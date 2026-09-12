"""API-level test: creating a Church or Fellowship is Super Admin only.
An `admin` is always scoped to the ONE organization they already manage
(see AdminOrganizationAssignment) - they must never be able to create a
second one, and a regular member can only join, never create."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db
from app.api.deps import get_current_user


@pytest.fixture()
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        app.dependency_overrides[get_current_user] = lambda: c.current_user
        yield c
    app.dependency_overrides.clear()


def _as(client, user):
    client.current_user = user


@pytest.mark.parametrize("path,payload", [
    ("/api/v1/community/church", {"name": "Grace Chapel", "privacy": "public"}),
    ("/api/v1/community/fellowship", {"name": "Young Adults", "privacy": "public"}),
])
def test_member_cannot_create_church_or_fellowship(client, make_user, path, payload):
    member = make_user(role="member")
    _as(client, member)
    resp = client.post(path, json=payload)
    assert resp.status_code == 403


@pytest.mark.parametrize("path,payload", [
    ("/api/v1/community/church", {"name": "Grace Chapel", "privacy": "public"}),
    ("/api/v1/community/fellowship", {"name": "Young Adults", "privacy": "public"}),
])
def test_org_admin_cannot_create_another_church_or_fellowship(client, make_user, path, payload):
    """An admin already manages exactly one organization - platform-wide
    creation is Super Admin only, never available to `admin`."""
    admin = make_user(role="admin")
    _as(client, admin)
    resp = client.post(path, json=payload)
    assert resp.status_code == 403


@pytest.mark.parametrize("path,payload", [
    ("/api/v1/community/church", {"name": "Grace Chapel", "privacy": "public"}),
    ("/api/v1/community/fellowship", {"name": "Young Adults", "privacy": "public"}),
])
def test_super_admin_can_create_church_or_fellowship(client, make_user, path, payload):
    super_admin = make_user(role="super_admin")
    _as(client, super_admin)
    resp = client.post(path, json=payload)
    assert resp.status_code == 200
    assert resp.json()["name"] == payload["name"]
