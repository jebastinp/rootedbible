"""
Converts a plan day's free-text Bible reference (e.g. "Genesis 1-3; Exodus 1")
into validated, structured ReadingPlanPassage rows - book_name/chapter_start/
chapter_end pairs checked against real bible_book records. This is the single
place that turns "Matthew 1-3" into something the app can deep-link into,
instead of the frontend regex-guessing it at render time. Book names are
looked up across any translation (book structure is assumed consistent across
translations in this schema), so a passage is valid independent of which
translation the reader eventually opens it in.
"""
import re

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationError
from app.models.bible import BibleBook
from app.models.reading_plan import ReadingPlan, ReadingPlanPassage

_SEGMENT_RE = re.compile(r"^\s*([1-3]?\s?[A-Za-z][A-Za-z ]*?)\s+(\d+)\s*(?:-\s*(\d+))?\s*$")


def _find_book(db: Session, name: str) -> BibleBook | None:
    return (
        db.query(BibleBook)
        .filter(BibleBook.name.ilike(name.strip()))
        .order_by(BibleBook.bible_version_id.asc())
        .first()
    )


def parse_passage_text(db: Session, text: str | None, testament: str) -> list[dict]:
    """Raises ValidationError if any segment doesn't resolve to a real book/chapter range."""
    if not text or not text.strip():
        return []

    passages: list[dict] = []
    for i, segment in enumerate(text.split(";")):
        segment = segment.strip()
        if not segment:
            continue
        match = _SEGMENT_RE.match(segment)
        if not match:
            raise ValidationError(
                f"Couldn't understand '{segment}' as a Bible reference (expected e.g. 'Genesis 1-3')."
            )
        book_name, start_str, end_str = match.groups()
        book = _find_book(db, book_name)
        if not book:
            raise ValidationError(f"'{book_name.strip()}' isn't a recognized Bible book.")
        chapter_start = int(start_str)
        chapter_end = int(end_str) if end_str else chapter_start
        if chapter_start < 1 or chapter_end < chapter_start:
            raise ValidationError(f"'{segment}' has an invalid chapter range.")
        if chapter_end > book.chapter_count:
            raise ValidationError(
                f"{book.name} only has {book.chapter_count} chapters - '{segment}' is out of range."
            )
        passages.append(
            {
                "testament": testament,
                "book_name": book.name,
                "chapter_start": chapter_start,
                "chapter_end": chapter_end,
                "sort_order": i,
            }
        )
    return passages


def sync_passages_for_plan(db: Session, plan: ReadingPlan) -> None:
    """Re-derives reading_plan_passage rows for `plan` from its old_testament/
    new_testament text. Call this every time those fields are written."""
    ot_passages = parse_passage_text(db, plan.old_testament, "OT")
    nt_passages = parse_passage_text(db, plan.new_testament, "NT")

    db.query(ReadingPlanPassage).filter(ReadingPlanPassage.reading_plan_id == plan.id).delete()
    sort_order = 0
    for passage in [*ot_passages, *nt_passages]:
        passage = {**passage, "sort_order": sort_order}
        sort_order += 1
        db.add(ReadingPlanPassage(reading_plan_id=plan.id, **passage))
    db.commit()
