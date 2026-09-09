import uuid
from datetime import datetime, date, timedelta

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ConflictError
from app.repositories.progress_repository import ProgressRepository
from app.repositories.reading_plan_repository import ReadingPlanRepository
from app.schemas.reading import (
    TodayReadingOut,
    MarkCompletedResponse,
    ProgressStatsOut,
    HeatmapEntry,
    MonthlyProgressPoint,
    PassageOut,
    PlanDayOut,
)


class ProgressService:
    """
    Owns all streak / completion-percentage / OT-NT breakdown calculations.
    Recalculation is triggered on: mark-as-completed, and after every CSV import.
    """

    def __init__(self, db: Session):
        self.db = db
        self.progress_repo = ProgressRepository(db)
        self.plan_repo = ReadingPlanRepository(db)

    # -----------------------------------------------------------------
    # HOME
    # -----------------------------------------------------------------
    def get_today_reading(self, user_id: uuid.UUID) -> TodayReadingOut:
        plan = self.plan_repo.get_today()
        if not plan:
            raise NotFoundError("No reading plan is scheduled for today yet.")
        entry = self.progress_repo.get(user_id, plan.id)
        passages = self.plan_repo.get_passages(plan.id)
        return TodayReadingOut(
            id=plan.id,
            day_number=plan.day_number,
            reading_date=plan.reading_date,
            old_testament=plan.old_testament,
            new_testament=plan.new_testament,
            estimated_minutes=plan.estimated_minutes,
            completed=bool(entry and entry.completed),
            completed_at=entry.completed_at if entry else None,
            passages=[PassageOut.model_validate(p) for p in passages],
        )

    def get_full_plan(self, user_id: uuid.UUID) -> list[PlanDayOut]:
        """Powers the member-facing 'View Full Plan' screen - every day in
        the church-wide plan plus this user's own completion status."""
        all_days = self.plan_repo.list_all_ordered()
        completed_days = {e.day_number for e in self.progress_repo.all_for_user(user_id) if e.completed}
        return [
            PlanDayOut(
                id=plan.id,
                day_number=plan.day_number,
                reading_date=plan.reading_date,
                old_testament=plan.old_testament,
                new_testament=plan.new_testament,
                estimated_minutes=plan.estimated_minutes,
                passages=[PassageOut.model_validate(p) for p in self.plan_repo.get_passages(plan.id)],
                completed=plan.day_number in completed_days,
            )
            for plan in all_days
        ]

    def mark_today_completed(self, user_id: uuid.UUID) -> MarkCompletedResponse:
        plan = self.plan_repo.get_today()
        if not plan:
            raise NotFoundError("No reading plan is scheduled for today yet.")

        entry = self.progress_repo.get_or_create(user_id, plan)
        if entry.completed:
            raise ConflictError("Today's reading is already marked as completed.")

        now = datetime.utcnow()
        self.progress_repo.mark_completed(entry, now)

        stats = self.recalculate_stats(user_id)

        return MarkCompletedResponse(
            day_number=plan.day_number,
            completed=True,
            completed_at=now,
            current_streak=stats.current_streak,
            longest_streak=stats.longest_streak,
            overall_percentage=float(stats.overall_percentage),
            days_completed=stats.days_completed,
        )

    # -----------------------------------------------------------------
    # RECALCULATION - the heart of the streak/percentage engine
    # -----------------------------------------------------------------
    def recalculate_stats(self, user_id: uuid.UUID):
        """
        Recomputes current streak, longest streak, days completed,
        OT/NT completed counts, and overall percentage for one user,
        purely from their reading_progress rows joined against the plan.
        Called after every mark-as-completed and after every CSV import.
        """
        all_plan_days = self.plan_repo.list_all_ordered()
        total_days = len(all_plan_days)
        entries = self.progress_repo.all_for_user(user_id)
        completed_by_day = {e.day_number: e for e in entries if e.completed}

        days_completed = len(completed_by_day)
        ot_completed = 0
        nt_completed = 0
        last_completed_date: date | None = None

        for plan_day in all_plan_days:
            entry = completed_by_day.get(plan_day.day_number)
            if entry:
                if plan_day.old_testament:
                    ot_completed += 1
                if plan_day.new_testament:
                    nt_completed += 1
                if not last_completed_date or plan_day.reading_date > last_completed_date:
                    last_completed_date = plan_day.reading_date

        # --- longest streak: walk the ordered day sequence once ---
        longest_streak = 0
        running_streak = 0
        for plan_day in all_plan_days:
            if plan_day.day_number in completed_by_day:
                running_streak += 1
                longest_streak = max(longest_streak, running_streak)
            else:
                running_streak = 0

        # --- current streak: count backwards from today (or yesterday if
        # today isn't marked yet) using day_number arithmetic. Day numbers
        # are a single consecutive sequence (1..N) for the whole plan, so
        # simple arithmetic is safe and avoids the "reset overwrites the
        # carried-forward streak" bug a single combined loop would have. ---
        today_plan = self.plan_repo.get_today()
        today_day_number = today_plan.day_number if today_plan else (all_plan_days[-1].day_number if all_plan_days else 0)

        current_streak = 0
        cursor = today_day_number if today_day_number in completed_by_day else today_day_number - 1
        while cursor in completed_by_day:
            current_streak += 1
            cursor -= 1

        overall_percentage = round((days_completed / total_days) * 100, 2) if total_days else 0.0

        stats = self.progress_repo.upsert_stats(
            user_id,
            current_streak=current_streak,
            longest_streak=longest_streak,
            days_completed=days_completed,
            ot_days_completed=ot_completed,
            nt_days_completed=nt_completed,
            overall_percentage=overall_percentage,
            last_completed_date=last_completed_date,
        )
        return stats

    # -----------------------------------------------------------------
    # PROGRESS PAGE
    # -----------------------------------------------------------------
    def _bible_progress(self, user_id: uuid.UUID) -> dict:
        """Derives real chapter- and book-level progress from the plan's own
        passages and this user's completed days - never hardcoded constants
        like 1,189 chapters or 66 books. A book counts 'completed' once every
        chapter the PLAN ever assigns from it (not the book's full canonical
        length - a partial plan, e.g. Gospels-only, should be completable)
        has been read; totals reflect the plan's actual Bible coverage."""
        completed_day_numbers = {e.day_number for e in self.progress_repo.all_for_user(user_id) if e.completed}
        book_chapters_assigned: dict[str, set] = {}
        book_chapters_read: dict[str, set] = {}

        for plan in self.plan_repo.list_all_ordered():
            for passage in self.plan_repo.get_passages(plan.id):
                assigned = book_chapters_assigned.setdefault(passage.book_name, set())
                assigned.update(range(passage.chapter_start, passage.chapter_end + 1))
                if plan.day_number in completed_day_numbers:
                    read = book_chapters_read.setdefault(passage.book_name, set())
                    read.update(range(passage.chapter_start, passage.chapter_end + 1))

        books_total = len(book_chapters_assigned)
        books_completed = sum(
            1 for name, assigned in book_chapters_assigned.items()
            if book_chapters_read.get(name, set()) >= assigned
        )
        chapters_total = sum(len(chapters) for chapters in book_chapters_assigned.values())
        chapters_completed = sum(len(chapters) for chapters in book_chapters_read.values())
        return {
            "books_completed": books_completed,
            "books_total": books_total,
            "chapters_completed": chapters_completed,
            "chapters_total": chapters_total,
        }

    def get_progress_stats(self, user_id: uuid.UUID) -> ProgressStatsOut:
        stats = self.progress_repo.get_stats(user_id) or self.recalculate_stats(user_id)
        total_days = self.plan_repo.total_days()
        ot_total = sum(1 for p in self.plan_repo.list_all_ordered() if p.old_testament)
        nt_total = sum(1 for p in self.plan_repo.list_all_ordered() if p.new_testament)
        bible_progress = self._bible_progress(user_id)
        return ProgressStatsOut(
            overall_percentage=float(stats.overall_percentage),
            current_streak=stats.current_streak,
            longest_streak=stats.longest_streak,
            days_completed=stats.days_completed,
            total_days=total_days,
            ot_days_completed=stats.ot_days_completed,
            nt_days_completed=stats.nt_days_completed,
            ot_total=ot_total,
            nt_total=nt_total,
            books_completed=bible_progress["books_completed"],
            books_total=bible_progress["books_total"],
            chapters_completed=bible_progress["chapters_completed"],
            chapters_total=bible_progress["chapters_total"],
            last_completed_date=stats.last_completed_date,
        )

    def get_heatmap(self, user_id: uuid.UUID) -> list[HeatmapEntry]:
        entries = self.progress_repo.all_for_user(user_id)
        plan_by_id = {p.id: p for p in self.plan_repo.list_all_ordered()}
        result = []
        for e in entries:
            plan = plan_by_id.get(e.reading_plan_id)
            if plan:
                result.append(HeatmapEntry(date=plan.reading_date, completed=e.completed))
        return result

    def get_monthly_progress(self, user_id: uuid.UUID) -> list[MonthlyProgressPoint]:
        entries = self.progress_repo.all_for_user(user_id)
        plan_by_id = {p.id: p for p in self.plan_repo.list_all_ordered()}
        month_totals: dict[str, int] = {}
        month_completed: dict[str, int] = {}

        for plan in plan_by_id.values():
            key = plan.reading_date.strftime("%Y-%m")
            month_totals[key] = month_totals.get(key, 0) + 1

        for e in entries:
            plan = plan_by_id.get(e.reading_plan_id)
            if plan and e.completed:
                key = plan.reading_date.strftime("%Y-%m")
                month_completed[key] = month_completed.get(key, 0) + 1

        points = []
        for key in sorted(month_totals.keys()):
            total = month_totals[key]
            completed = month_completed.get(key, 0)
            pct = round((completed / total) * 100, 2) if total else 0.0
            points.append(MonthlyProgressPoint(month=key, completion_percentage=pct))
        return points

    # -----------------------------------------------------------------
    # ADMIN REPORTS (church-wide aggregate counts only - never exposed to
    # normal members as a global "who's reading" list; see Community's
    # circle-scoped membership model for member-facing group progress).
    # -----------------------------------------------------------------
    def todays_readers_count(self) -> int:
        return self.progress_repo.todays_readers_count(date.today())
