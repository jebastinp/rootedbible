import re

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.repositories.bible_repository import BibleRepository
from app.schemas.bible import BibleVersionOut, BibleBookOut, BibleChapterOut, ChapterNav, VerseOut, SearchResultOut, SearchResponseOut

# Matches "John 3:16", "John 3", "1 Corinthians 13", "Psalm 23:1" etc.
_REFERENCE_RE = re.compile(r"^\s*([1-3]?\s?[A-Za-z][A-Za-z ]*?)\s+(\d+)(?::(\d+))?\s*$")


class BibleContentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = BibleRepository(db)

    def list_versions(self) -> list[BibleVersionOut]:
        return [BibleVersionOut.model_validate(v) for v in self.repo.list_versions()]

    def list_books(self, version_code: str) -> list[BibleBookOut]:
        version = self.repo.get_version_by_code(version_code)
        if not version:
            raise NotFoundError(f"Bible version '{version_code}' not found")
        return [BibleBookOut.model_validate(b) for b in self.repo.list_books(version.id)]

    def get_chapter(self, version_code: str, book_name: str, chapter_number: int) -> BibleChapterOut:
        version = self.repo.get_version_by_code(version_code)
        if not version:
            raise NotFoundError(f"Bible version '{version_code}' not found")

        book = self.repo.get_book_by_name(version.id, book_name)
        if not book:
            raise NotFoundError(f"Book '{book_name}' not found in {version.version_name}")

        chapter = self.repo.get_chapter(book.id, chapter_number)
        if not chapter:
            raise NotFoundError(f"{book_name} {chapter_number} not found in {version.version_name}")

        return BibleChapterOut(
            id=chapter.id,
            book_id=book.id,
            book_name=book.name,
            chapter_number=chapter.chapter_number,
            verses=[VerseOut.model_validate(v) for v in chapter.verses],
            total_chapters_in_book=book.chapter_count,
        )

    def get_navigation(self, version_code: str, book_name: str, chapter_number: int) -> ChapterNav:
        version = self.repo.get_version_by_code(version_code)
        if not version:
            raise NotFoundError(f"Bible version '{version_code}' not found")
        books = self.repo.list_books(version.id)
        book = next((b for b in books if b.name.lower() == book_name.lower()), None)
        if not book:
            raise NotFoundError(f"Book '{book_name}' not found")

        nav = ChapterNav()
        if chapter_number > 1:
            nav.previous = {"book": book.name, "chapter": chapter_number - 1}
        elif book.sort_order > 1:
            prev_book = next((b for b in books if b.sort_order == book.sort_order - 1), None)
            if prev_book:
                nav.previous = {"book": prev_book.name, "chapter": prev_book.chapter_count}

        if chapter_number < book.chapter_count:
            nav.next = {"book": book.name, "chapter": chapter_number + 1}
        else:
            next_book = next((b for b in books if b.sort_order == book.sort_order + 1), None)
            if next_book:
                nav.next = {"book": next_book.name, "chapter": 1}

        return nav

    def search(self, version_code: str, query: str, limit: int = 30) -> SearchResponseOut:
        version = self.repo.get_version_by_code(version_code)
        if not version:
            raise NotFoundError(f"Bible version '{version_code}' not found")

        query = query.strip()
        if not query:
            return SearchResponseOut(query=query, results=[])

        resolved_reference = None
        match = _REFERENCE_RE.match(query)
        if match:
            book_name, chapter_str, verse_str = match.groups()
            book = self.repo.get_book_by_name(version.id, book_name.strip())
            if book and 1 <= int(chapter_str) <= book.chapter_count:
                resolved_reference = {
                    "book": book.name,
                    "chapter": int(chapter_str),
                    "verse": int(verse_str) if verse_str else None,
                }

        verses = self.repo.search_verses(version.id, query, limit=limit)
        results = [
            SearchResultOut(
                verse_id=v.id,
                book_name=v.chapter.book.name,
                chapter_number=v.chapter.chapter_number,
                verse_number=v.verse_number,
                text=v.text,
            )
            for v in verses
        ]
        return SearchResponseOut(query=query, resolved_reference=resolved_reference, results=results)
