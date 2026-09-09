"""
Verifies a Supabase Auth session token.

Supabase projects sign session tokens one of two ways depending on when/how
they were set up:
  - Newer projects (and any project with "JWT Signing Keys" enabled) sign
    with an asymmetric key (ES256/RS256) and publish the public keys at
    /auth/v1/.well-known/jwks.json.
  - Older projects sign with a single shared secret (HS256) - the "Legacy
    JWT Secret" found in Project Settings -> API -> JWT Settings.

We support both rather than guessing, since this is a per-project setting
we can't control from application code.
"""
import time

import httpx
from jose import jwt

from app.core.config import settings

_jwks_cache: dict = {"keys": [], "fetched_at": 0.0}
_CACHE_TTL_SECONDS = 3600


def _fetch_jwks() -> list[dict]:
    url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
    response = httpx.get(url, timeout=10)
    response.raise_for_status()
    return response.json().get("keys", [])


def _get_jwks(force_refresh: bool = False) -> list[dict]:
    now = time.time()
    if force_refresh or not _jwks_cache["keys"] or now - _jwks_cache["fetched_at"] > _CACHE_TTL_SECONDS:
        _jwks_cache["keys"] = _fetch_jwks()
        _jwks_cache["fetched_at"] = now
    return _jwks_cache["keys"]


class SupabaseTokenError(Exception):
    pass


def verify_supabase_access_token(token: str) -> dict:
    try:
        header = jwt.get_unverified_header(token)
    except Exception as exc:
        raise SupabaseTokenError("Malformed token") from exc

    alg = header.get("alg")

    try:
        if alg == "HS256":
            return jwt.decode(token, settings.SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated")

        kid = header.get("kid")
        keys = _get_jwks()
        match = next((k for k in keys if k.get("kid") == kid), None)
        if not match:
            # Key may have rotated since our last fetch - refresh once and retry.
            keys = _get_jwks(force_refresh=True)
            match = next((k for k in keys if k.get("kid") == kid), None)
        if not match:
            raise SupabaseTokenError("No matching Supabase signing key found")

        return jwt.decode(token, match, algorithms=[alg], audience="authenticated")
    except SupabaseTokenError:
        raise
    except Exception as exc:
        raise SupabaseTokenError(str(exc)) from exc
