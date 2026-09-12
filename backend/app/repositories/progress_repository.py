import uuid
from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.progress import ReadingProgress, UserStats
from app.models.reading_plan import ReadingPlan
from app.models.user import User, UserRole

# Platform staff accounts (e.g. the seeded ADMIN001 super admin) manage Rooted -
# they are not participants and must never appear ranked alongside real readers.
_STAFF_ROLES = (UserRole.admin, UserRole.super_admin)


class ProgressRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: uuid.UUID, reading_plan_id: uuid.UUID) -> ReadingProgress | None:
        return (
            self.db.query(ReadingProgress)
            .filter(ReadingProgress.user_id == user_id, ReadingProgress.reading_plan_id == reading_plan_id)
            .first()
        )

    def get_or_create(self, user_id: uuid.UUID, reading_plan: ReadingPlan) -> ReadingProgress:
        entry = self.get(user_id, reading_plan.id)
        if entry:
            return entry
        entry = ReadingProgress(user_id=user_id, reading_plan_id=reading_plan.id, day_number=reading_plan.day_number)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def all_for_user(self, user_id: uuid.UUID, scope_key: str | None = None) -> list[ReadingProgress]:
        """scope_key restricts results to progress against ONE calendar
        (platform / a specific Church's / a specific Fellowship's) - day
        numbers are only unique within a scope, so mixing scopes here would
        silently corrupt streak/percentage math for a member who switches
        their active calendar."""
        query = self.db.query(ReadingProgress).filter(ReadingProgress.user_id == user_id)
        if scope_key is not None:
            query = query.join(ReadingPlan, ReadingPlan.id == ReadingProgress.reading_plan_id).filter(ReadingPlan.scope_key == scope_key)
        return query.order_by(ReadingProgress.day_number.asc()).all()

    def completed_for_user(self, user_id: uuid.UUID) -> list[ReadingProgress]:
        return (
            self.db.query(ReadingProgress)
            .filter(ReadingProgress.user_id == user_id, ReadingProgress.completed.is_(True))
            .order_by(ReadingProgress.day_number.asc())
            .all()
        )

    def mark_completed(self, entry: ReadingProgress, completed_at) -> ReadingProgress:
        entry.completed = True
        entry.completed_at = completed_at
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_stats(self, user_id: uuid.UUID) -> UserStats | None:
        return self.db.query(UserStats).filter(UserStats.user_id == user_id).first()

    def upsert_stats(self, user_id: uuid.UUID, **kwargs) -> UserStats:
        stats = self.get_stats(user_id)
        if not stats:
            stats = UserStats(user_id=user_id)
            self.db.add(stats)
        for key, value in kwargs.items():
            setattr(stats, key, value)
        self.db.commit()
        self.db.refresh(stats)
        return stats

    def todays_readers_count(self, today: date) -> int:
        return (
            self.db.query(func.count(func.distinct(ReadingProgress.user_id)))
            .join(ReadingPlan, ReadingPlan.id == ReadingProgress.reading_plan_id)
            .join(User, User.id == ReadingProgress.user_id)
            .filter(
                ReadingPlan.reading_date == today,
                ReadingProgress.completed.is_(True),
                User.deleted_at.is_(None),
                User.role.notin_(_STAFF_ROLES),
            )
            .scalar()
            or 0
        )

    def top_readers(self, limit: int = 5) -> list[tuple[User, UserStats]]:
        return (
            self.db.query(User, UserStats)
            .join(UserStats, UserStats.user_id == User.id)
            .filter(User.deleted_at.is_(None), User.role.notin_(_STAFF_ROLES))
            .order_by(desc(UserStats.current_streak), desc(UserStats.days_completed))
            .limit(limit)
            .all()
        )

    def leaderboard(self, page: int = 1, page_size: int = 50) -> tuple[list[tuple[User, UserStats]], int]:
        query = (
            self.db.query(User, UserStats)
            .join(UserStats, UserStats.user_id == User.id)
            .filter(User.deleted_at.is_(None), User.role.notin_(_STAFF_ROLES))
        )
        total = query.count()
        items = (
            query.order_by(desc(UserStats.current_streak), desc(UserStats.days_completed))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total
