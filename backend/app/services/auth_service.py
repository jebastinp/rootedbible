from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.core.security import create_access_token, create_refresh_token, decode_token, TokenError
from app.core.supabase_auth import verify_supabase_access_token, SupabaseTokenError
from app.core.supabase_admin import sync_role_to_supabase
from app.models.user import UserRole, UserStatus
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
        self._enforce_permanent_super_admin(user)
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

        self._enforce_permanent_super_admin(user)
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
    def _enforce_permanent_super_admin(user) -> None:
        """These emails always have full platform-wide Super Admin control -
        self-heals every login, regardless of whatever role the account
        happens to have in the database right now."""
        permanent_emails = {e.strip().lower() for e in settings.PERMANENT_SUPER_ADMIN_EMAILS}
        if user.email and user.email.strip().lower() in permanent_emails:
            user.role = UserRole.super_admin
            user.status = UserStatus.active

    def _issue_tokens(self, user) -> TokenResponse:
        access_token = create_access_token(subject=str(user.id), role=user.role.value, extra_claims={"user_code": user.user_id})
        refresh_token = create_refresh_token(subject=str(user.id))
        admin_orgs = self._list_admin_orgs(user.id)
        sync_role_to_supabase(user.supabase_user_id, user.role.value, [org.model_dump(mode="json") for org in admin_orgs])
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserOut.model_validate(user),
            admin_orgs=admin_orgs,
        )

    def _list_admin_orgs(self, user_id) -> list:
        """The ONE Church/Fellowship this user administers, if any - see
        AdminOrganizationAssignment, the single source of truth for
        org-level ADMIN status. Returns at most one entry: an `admin`
        manages exactly one organization, never more."""
        from app.schemas.user import AdminOrgOut
        from app.models.admin_assignment import AdminOrganizationAssignment
        from app.models.church import Church
        from app.models.fellowship import Fellowship

        assignment = self.db.query(AdminOrganizationAssignment).filter(AdminOrganizationAssignment.user_id == user_id).first()
        if not assignment:
            return []
        if assignment.organization_type == "church":
            church = self.db.query(Church).filter(Church.id == assignment.church_id).first()
            return [AdminOrgOut(kind="church", org_id=church.id, name=church.name)] if church else []
        fellowship = self.db.query(Fellowship).filter(Fellowship.id == assignment.fellowship_id).first()
        return [AdminOrgOut(kind="fellowship", org_id=fellowship.id, name=fellowship.name)] if fellowship else []

    def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except TokenError:
            raise UnauthorizedError("Invalid or expired refresh token")
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")

        import uuid as uuid_lib
        user = self.users.get_by_id(uuid_lib.UUID(payload["sub"]))
        if not user:
            raise UnauthorizedError("User not found or inactive")
        self._enforce_permanent_super_admin(user)
        if user.status != UserStatus.active:
            raise UnauthorizedError("User not found or inactive")
        self.db.commit()

        return self._issue_tokens(user)
