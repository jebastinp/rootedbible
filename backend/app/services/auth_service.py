from datetime import datetime

from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.core.security import create_access_token, create_refresh_token, decode_token, TokenError
from app.core.supabase_auth import verify_supabase_access_token, SupabaseTokenError
from app.models.user import UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.user import TokenResponse, UserOut


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def login(self, user_code: str) -> TokenResponse:
        user = self.users.get_by_user_code(user_code.strip())
        if not user:
            raise UnauthorizedError("User ID not found. Please check with your church admin.")
        self._check_status(user)
        user = self.users.update(user, last_login_at=datetime.utcnow(), auth_provider=user.auth_provider or "legacy")
        return self._issue_tokens(user)

    def login_with_supabase(self, supabase_access_token: str) -> TokenResponse:
        """Verifies the session token supabase-js hands back after either
        signInWithOAuth(google) or signInWithPassword/signUp (email+password)
        and syncs it to a Rooted user. Supabase issues this token itself once
        it has already authenticated the user (OAuth handshake, or password +
        its own email-verification requirement) - we only ever verify
        Supabase's own signature, never Google's or the password directly."""
        try:
            payload = verify_supabase_access_token(supabase_access_token)
        except SupabaseTokenError:
            raise UnauthorizedError("Your sign-in session could not be verified. Please sign in again.")

        email = payload.get("email")
        if not email:
            raise UnauthorizedError("Your account has no email address Rooted can use.")

        metadata = payload.get("user_metadata") or {}
        provider = (payload.get("app_metadata") or {}).get("provider") or "email"
        supabase_user_id = payload["sub"]
        name = metadata.get("full_name") or metadata.get("name") or email.split("@")[0]
        picture = metadata.get("avatar_url") or metadata.get("picture")
        phone = metadata.get("phone") or None
        date_of_birth = self._parse_date(metadata.get("date_of_birth"))

        is_new = False
        user = self.users.get_by_supabase_user_id(supabase_user_id)
        if not user:
            user = self.users.get_by_email(email)
            if user:
                user = self.users.update(user, supabase_user_id=supabase_user_id, photo_url=user.photo_url or picture)
            else:
                first_name = (name or email.split("@")[0]).split()[0]
                user = self.users.create_with_unique_id(
                    first_name,
                    supabase_user_id=supabase_user_id,
                    email=email,
                    name=name,
                    photo_url=picture,
                    phone=phone,
                    date_of_birth=date_of_birth,
                    auth_provider=provider,
                )
                is_new = True

        self._check_status(user)
        user = self.users.update(user, last_login_at=datetime.utcnow())
        response = self._issue_tokens(user)
        response.is_new_user = is_new
        # Onboarding is now a lightweight welcome/choice screen (explore the
        # Bible vs. start a plan), so every brand-new account sees it once -
        # it's no longer gated on missing profile fields.
        response.needs_onboarding = is_new
        return response

    @staticmethod
    def _parse_date(value):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _check_status(user) -> None:
        if user.status == UserStatus.suspended:
            raise ForbiddenError("This account has been suspended. Please contact your church admin.")
        if user.status == UserStatus.inactive:
            raise ForbiddenError("This account is inactive. Please contact your church admin.")

    @staticmethod
    def _issue_tokens(user) -> TokenResponse:
        access_token = create_access_token(subject=str(user.id), role=user.role.value, extra_claims={"user_code": user.user_id})
        refresh_token = create_refresh_token(subject=str(user.id))
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserOut.model_validate(user),
        )

    def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except TokenError:
            raise UnauthorizedError("Invalid or expired refresh token")
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")

        import uuid as uuid_lib
        user = self.users.get_by_id(uuid_lib.UUID(payload["sub"]))
        if not user or user.status != UserStatus.active:
            raise UnauthorizedError("User not found or inactive")

        access_token = create_access_token(subject=str(user.id), role=user.role.value, extra_claims={"user_code": user.user_id})
        new_refresh_token = create_refresh_token(subject=str(user.id))
        return TokenResponse(access_token=access_token, refresh_token=new_refresh_token, user=UserOut.model_validate(user))
