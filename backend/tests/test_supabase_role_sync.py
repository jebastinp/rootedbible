"""Unit tests for syncing a user's Rooted role/admin-org status into
Supabase's own auth.users.app_metadata, so it's visible directly in the
Supabase dashboard - never blocks or fails a real login on error."""
from unittest.mock import patch

from app.core.config import settings
from app.core.supabase_admin import sync_role_to_supabase


def test_noop_when_no_supabase_user_id():
    with patch("app.core.supabase_admin.httpx.put") as mock_put:
        sync_role_to_supabase(None, "member", [])
        mock_put.assert_not_called()


def test_noop_when_supabase_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_URL", "")
    monkeypatch.setattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")
    with patch("app.core.supabase_admin.httpx.put") as mock_put:
        sync_role_to_supabase("some-supabase-id", "super_admin", [])
        mock_put.assert_not_called()


def test_calls_supabase_admin_api_with_role_and_admin_orgs(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
    with patch("app.core.supabase_admin.httpx.put") as mock_put:
        sync_role_to_supabase("some-supabase-id", "admin", [{"kind": "church", "org_id": "abc", "name": "Grace Chapel"}])

        mock_put.assert_called_once()
        _, kwargs = mock_put.call_args
        assert kwargs["json"]["app_metadata"]["rooted_role"] == "admin"
        assert kwargs["json"]["app_metadata"]["rooted_admin_orgs"][0]["name"] == "Grace Chapel"
        assert kwargs["headers"]["apikey"] == "test-service-role-key"
        assert "some-supabase-id" in mock_put.call_args[0][0]


def test_never_raises_even_if_the_http_call_fails(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
    with patch("app.core.supabase_admin.httpx.put", side_effect=RuntimeError("network down")):
        sync_role_to_supabase("some-supabase-id", "member", [])  # must not raise
