"""API-level test: creating a Church or Fellowship is admin-only.
A regular member can only join one, never create one - enforced by
`require_admin` on POST /community/church and /community/fellowship."""
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
def test_admin_can_create_church_or_fellowship(client, make_user, path, payload):
    admin = make_user(role="admin")
    _as(client, admin)
    resp = client.post(path, json=payload)
    assert resp.status_code == 200
    assert resp.json()["name"] == payload["name"]
