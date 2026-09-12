"""Best-effort sync of a user's Rooted role/admin status INTO Supabase's
own auth.users table (app_metadata), so it's visible directly in the
Supabase dashboard (Authentication -> Users) without cross-referencing
Rooted's own Postgres `users` table. Never raises: a sync failure (missing
Supabase admin credentials, network hiccup, user not yet linked to a
Supabase account) must never block sign-in - it's a convenience mirror,
not a source of truth. Rooted's own `users` table remains authoritative."""
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger("rooted")


def sync_role_to_supabase(supabase_user_id: str | None, role: str, admin_orgs: list[dict]) -> None:
    if not supabase_user_id or not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        return
    try:
        url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/admin/users/{supabase_user_id}"
        httpx.put(
            url,
            headers={
                "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "app_metadata": {
                    "rooted_role": role,
                    "rooted_admin_orgs": admin_orgs,
                }
            },
            timeout=5,
        )
    except Exception:
        logger.warning("Could not sync role to Supabase for user %s", supabase_user_id, exc_info=True)
