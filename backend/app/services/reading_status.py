"""Shared "did this user read today" check, reused by every community
surface (challenge / family / buddy) so there is exactly one definition of
"completed today" - never a parallel calculation per feature."""
import uuid
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models.progress import ReadingProgress
from app.models.reading_plan import ReadingPlan
from app.models.bible_engagement import ReadingCompletion


def completed_today_user_ids(db: Session, user_ids: list[uuid.UUID]) -> set[uuid.UUID]:
    if not user_ids:
        return set()
    today = date.today()
    completed: set[uuid.UUID] = set()

    plan_rows = (
        db.query(ReadingProgress.user_id)
        .join(ReadingPlan, ReadingPlan.id == ReadingProgress.reading_plan_id)
        .filter(
            ReadingProgress.user_id.in_(user_ids),
            ReadingProgress.completed.is_(True),
            ReadingPlan.reading_date == today,
        )
        .all()
    )
    completed.update(r[0] for r in plan_rows)

    completion_rows = (
        db.query(ReadingCompletion.user_id)
        .filter(
            ReadingCompletion.user_id.in_(user_ids),
            ReadingCompletion.completed_at >= datetime.combine(today, datetime.min.time()),
        )
        .all()
    )
    completed.update(r[0] for r in completion_rows)
    return completed
