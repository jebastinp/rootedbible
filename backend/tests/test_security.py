import pytest
from datetime import timedelta

from app.core.security import create_access_token, create_refresh_token, decode_token, TokenError


def test_access_token_roundtrip():
    token = create_access_token(subject="user-123", role="member")
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["role"] == "member"
    assert payload["type"] == "access"


def test_refresh_token_roundtrip():
    token = create_refresh_token(subject="user-123")
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["type"] == "refresh"


def test_invalid_token_raises():
    with pytest.raises(TokenError):
        decode_token("not-a-real-token")


def test_extra_claims_are_embedded():
    token = create_access_token(subject="user-123", role="admin", extra_claims={"user_code": "REH001"})
    payload = decode_token(token)
    assert payload["user_code"] == "REH001"
    assert payload["role"] == "admin"
