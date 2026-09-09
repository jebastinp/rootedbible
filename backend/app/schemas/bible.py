import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BibleVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    code: str
    language: str
    version_name: str
    license_status: str


class BibleBookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    testament: str
    sort_order: int
    chapter_count: int


class VerseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    verse_number: int
    text: str


class BibleChapterOut(BaseModel):
    id: uuid.UUID
    book_id: uuid.UUID
    book_name: str
    chapter_number: int
    verses: list[VerseOut]
    total_chapters_in_book: int


class ChapterNav(BaseModel):
    """Lets the reading screen show Previous/Next chapter without another lookup round-trip."""
    previous: Optional[dict] = None  # {"book": "Genesis", "chapter": 1}
    next: Optional[dict] = None


class SearchResultOut(BaseModel):
    verse_id: uuid.UUID
    book_name: str
    chapter_number: int
    verse_number: int
    text: str


class SearchResponseOut(BaseModel):
    query: str
    # If the query looked like a reference ("John 3:16", "Psalm 23"), jump straight there.
    resolved_reference: Optional[dict] = None  # {"book": "John", "chapter": 3, "verse": 16}
    results: list[SearchResultOut]
