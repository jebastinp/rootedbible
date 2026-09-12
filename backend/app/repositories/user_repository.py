import uuid
from datetime import datetime, date

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User, UserRole, UserStatus
from app.models.progress import UserStats


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()

    def get_by_user_code(self, user_code: str) -> User | None:
        return self.db.query(User).filter(func.upper(User.user_id) == user_code.upper(), User.deleted_at.is_(None)).first()

    def get_by_supabase_user_id(self, supabase_user_id: str) -> User | None:
        return self.db.query(User).filter(User.supabase_user_id == supabase_user_id, User.deleted_at.is_(None)).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(func.lower(User.email) == email.lower(), User.deleted_at.is_(None)).first()

    @staticmethod
    def _rooted_id_prefix(first_name: str) -> str:
        """Normalizes a first name into the Rooted ID prefix: uppercase,
        alphanumeric only, first 4 characters (or fewer if the name is
        shorter). 'Jebastin' -> 'JEBA', 'Sam' -> 'SAM', 'Li' -> 'LI'."""
        normalized = "".join(ch for ch in first_name.upper() if ch.isalnum())
        return normalized[:4] or "USER"

    def generate_unique_user_id(self, first_name: str) -> str:
        """Next free ROOTED ID for this name's prefix (JEBA001, JEBA002, ...).
        This check-then-use approach is a good first guess, but is NOT
        sufficient for concurrency safety on its own - see
        create_with_unique_id(), which retries with a fresh candidate on a
        genuine collision at insert time (the user_id column is UNIQUE),
        rather than trusting this pre-check alone under concurrent signups."""
        prefix = self._rooted_id_prefix(first_name)
        existing = {
            row[0] for row in self.db.query(User.user_id).filter(User.user_id.like(f"{prefix}%")).all()
        }
        for seq in range(1, 1000):
            candidate = f"{prefix}{seq:03d}"
            if candidate not in existing:
                return candidate
        # Extremely unlikely (1000 people sharing the same 4-letter prefix) -
        # fail loudly rather than silently producing a malformed/duplicate id.
        raise ValueError(f"No free Rooted ID sequence left for prefix '{prefix}'")

    def create_with_unique_id(self, first_name: str, **kwargs) -> User:
        """Creates a user with a fresh, race-condition-safe Rooted ID:
        retries with the next candidate if a concurrent signup already took
        the one we picked (caught via the user_id UNIQUE constraint), instead
        of relying solely on the pre-insert existence check."""
        last_error: IntegrityError | None = None
        for _ in range(5):
            candidate = self.generate_unique_user_id(first_name)
            try:
                return self.create(user_id=candidate, **kwargs)
            except IntegrityError as exc:
                self.db.rollback()
                last_error = exc
        raise last_error or RuntimeError("Could not allocate a unique Rooted ID")

    def list(
        self,
        search: str | None = None,
        role: UserRole | None = None,
        status_filter: UserStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[User], int]:
        query = self.db.query(User).filter(User.deleted_at.is_(None))
        if search:
            like = f"%{search}%"
            query = query.filter((User.name.ilike(like)) | (User.user_id.ilike(like)) | (User.phone.ilike(like)))
        if role:
            query = query.filter(User.role == role)
        if status_filter:
            query = query.filter(User.status == status_filter)

        total = query.count()
        items = (
            query.order_by(User.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def create(self, **kwargs) -> User:
        user = User(**kwargs)
        self.db.add(user)
        self.db.flush()
        # ensure stats row exists
        self.db.add(UserStats(user_id=user.id))
        self._resolve_pending_admin_invites(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def _resolve_pending_admin_invites(self, user: User) -> None:
        """If a Church/Fellowship admin was pre-provisioned by this exact
        email before they ever signed up (see CommunityService.
        _resolve_admin_assignment / invite_admin_by_email), turn that
        pending invite into a real owner/admin membership now that the
        account exists. Every self-serve signup and admin-created member
        funnels through this one create() method, so this is the single
        place that needs to run this check."""
        if not user.email:
            return
        from app.models.church import Church, ChurchMember
        from app.models.fellowship import Fellowship, FellowshipMember

        normalized = user.email.strip().lower()
        for church in self.db.query(Church).filter(Church.pending_admin_email == normalized).all():
            existing = self.db.query(ChurchMember).filter(ChurchMember.church_id == church.id, ChurchMember.user_id == user.id).first()
            if existing:
                existing.status = "active"
                existing.role = "owner"
            else:
                self.db.add(ChurchMember(church_id=church.id, user_id=user.id, role="owner", status="active"))
            church.owner_id = user.id
            church.pending_admin_email = None

        for fellowship in self.db.query(Fellowship).filter(Fellowship.pending_admin_email == normalized).all():
            existing = self.db.query(FellowshipMember).filter(FellowshipMember.fellowship_id == fellowship.id, FellowshipMember.user_id == user.id).first()
            if existing:
                existing.status = "active"
                existing.role = "owner"
            else:
                self.db.add(FellowshipMember(fellowship_id=fellowship.id, user_id=user.id, role="owner", status="active"))
            fellowship.owner_id = user.id
            fellowship.pending_admin_email = None

    def update(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            if value is not None:
                setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def soft_delete(self, user: User) -> None:
        user.deleted_at = datetime.utcnow()
        user.status = UserStatus.inactive
        self.db.commit()

    def count_active(self) -> int:
        return self.db.query(User).filter(User.deleted_at.is_(None), User.status == UserStatus.active).count()

    def get_stats(self, user_id: uuid.UUID) -> UserStats | None:
        return self.db.query(UserStats).filter(UserStats.user_id == user_id).first()
