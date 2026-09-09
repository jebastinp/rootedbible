import uuid
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.repositories.bible_repository import BibleRepository
from app.repositories.reading_plan_repository import ReadingPlanRepository
from app.models.bible import BibleBook
from app.services.passage_parser import sync_passages_for_plan
from app.schemas.plan_generator import (
    PlanGenerateRequest,
    PlanCommitRequest,
    PlanDayPreview,
    PlanPreviewResponse,
)


class PlanGeneratorService:
    """
    Implements product-plan section 5 (Reading Plan Logic):
    daily_chapters = total_chapters / available_reading_days, with the
    remainder spread across extra days rather than piled onto the last one,
    and never overloading a single day. Rest days are skipped entirely
    rather than double-loaded onto the next reading day.
    """

    def __init__(self, db: Session):
        self.db = db
        self.bible_repo = BibleRepository(db)
        self.plan_repo = ReadingPlanRepository(db)

    def _books_in_scope(self, req: PlanGenerateRequest) -> list[BibleBook]:
        version = self.bible_repo.get_version_by_code(req.bible_version_code)
        if not version:
            raise NotFoundError(f"Bible version '{req.bible_version_code}' not found")

        all_books = self.bible_repo.list_books(version.id)
        if req.section == "full_bible":
            return all_books
        if req.section == "new_testament":
            return [b for b in all_books if b.testament == "NT"]
        if req.section == "gospels":
            wanted = {"matthew", "mark", "luke", "john"}
            return [b for b in all_books if b.name.lower() in wanted]
        if req.section == "psalms":
            return [b for b in all_books if b.name.lower() == "psalms"]
        if req.section == "custom":
            if not req.custom_books:
                raise ValidationError("custom_books is required when section is 'custom'")
            wanted = {n.lower() for n in req.custom_books}
            books = [b for b in all_books if b.name.lower() in wanted]
            if not books:
                raise ValidationError("None of the requested custom_books were found in this Bible version")
            return books
        raise ValidationError(f"Unknown section '{req.section}'")

    @staticmethod
    def _is_rest_day(day_index: int, calendar_date: date, rest_day: str) -> bool:
        """day_index is 1-based day number within the plan."""
        if rest_day == "none":
            return False
        if rest_day == "sunday":
            return calendar_date.weekday() == 6  # Monday=0 ... Sunday=6
        if rest_day == "one_per_week":
            return day_index % 7 == 0
        return False

    @staticmethod
    def _format_chunk(entries: list[tuple[str, int]]) -> str:
        """entries: list of (book_name, chapter_number), already in reading order.
        Groups consecutive same-book chapters into 'Book start-end' / 'Book n'."""
        if not entries:
            return ""
        parts: list[str] = []
        book, start = entries[0]
        prev = start
        for b, c in entries[1:]:
            if b == book and c == prev + 1:
                prev = c
                continue
            parts.append(f"{book} {start}" if start == prev else f"{book} {start}-{prev}")
            book, start, prev = b, c, c
        parts.append(f"{book} {start}" if start == prev else f"{book} {start}-{prev}")
        return "; ".join(parts)

    def _build_days(self, req: PlanGenerateRequest) -> tuple[list[PlanDayPreview], int]:
        books = self._books_in_scope(req)
        # Flatten to one (book_name, testament, chapter_number) tuple per chapter, canonical order.
        flat: list[tuple[str, str, int]] = []
        for book in books:
            for ch in range(1, book.chapter_count + 1):
                flat.append((book.name, book.testament, ch))
        total_chapters = len(flat)
        if total_chapters == 0:
            raise ValidationError("Selected scope has no chapters available - check the Bible content is seeded")

        # Work out which calendar days are reading days vs rest days first.
        day_dates = [req.start_date + timedelta(days=i) for i in range(req.duration_days)]
        is_rest = [self._is_rest_day(i + 1, d, req.rest_day) for i, d in enumerate(day_dates)]
        reading_days = req.duration_days - sum(is_rest)
        if reading_days <= 0:
            raise ValidationError("Every day in this range is a rest day - widen the duration or change the rest-day setting")

        # daily_chapters = total_chapters / available_reading_days, remainder
        # spread across the first N reading days rather than the last one.
        base = total_chapters // reading_days
        remainder = total_chapters % reading_days
        chapters_per_reading_day = [base + 1 if i < remainder else base for i in range(reading_days)]

        days: list[PlanDayPreview] = []
        cursor = 0
        reading_day_pointer = 0
        for i, d in enumerate(day_dates):
            if is_rest[i]:
                days.append(PlanDayPreview(day_number=i + 1, reading_date=d, is_rest_day=True))
                continue

            n = chapters_per_reading_day[reading_day_pointer]
            reading_day_pointer += 1
            chunk = flat[cursor: cursor + n]
            cursor += n

            ot_entries = [(b, c) for b, t, c in chunk if t == "OT"]
            nt_entries = [(b, c) for b, t, c in chunk if t == "NT"]
            days.append(
                PlanDayPreview(
                    day_number=i + 1,
                    reading_date=d,
                    old_testament=self._format_chunk(ot_entries) or None,
                    new_testament=self._format_chunk(nt_entries) or None,
                    is_rest_day=False,
                )
            )

        return days, total_chapters

    def preview(self, req: PlanGenerateRequest) -> PlanPreviewResponse:
        days, total_chapters = self._build_days(req)
        reading_days = sum(1 for d in days if not d.is_rest_day)
        return PlanPreviewResponse(
            total_days=req.duration_days,
            reading_days=reading_days,
            rest_days=req.duration_days - reading_days,
            total_chapters=total_chapters,
            approx_chapters_per_day=round(total_chapters / reading_days, 1) if reading_days else 0,
            days=days,
        )

    def commit(self, req: PlanCommitRequest, replace_existing: bool = True) -> int:
        """Writes the generated plan into `reading_plan` (skipping rest days -
        those simply have no row, same as today's admin-authored plan).
        Returns number of rows written.

        IMPORTANT: `day_number` is globally unique in `reading_plan`, and this
        generator always numbers its output starting at 1. So replace_existing
        wipes the ENTIRE existing plan table before writing the new one -
        this is meant for "start a new church-wide challenge", not for
        patching a few days into an existing plan. The admin UI must warn
        the user about this before calling commit.
        """
        days, _ = self._build_days(req)

        if replace_existing:
            for plan in self.plan_repo.list_all_ordered():
                self.plan_repo.delete(plan)

        written = 0
        for d in days:
            if d.is_rest_day:
                continue
            plan = self.plan_repo.create(
                day_number=d.day_number,
                reading_date=d.reading_date,
                old_testament=d.old_testament,
                new_testament=d.new_testament,
                estimated_minutes=15,
            )
            sync_passages_for_plan(self.db, plan)
            written += 1
        return written
