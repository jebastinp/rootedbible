import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.bible_engagement import Bookmark, ReadingPosition, ReadingCompletion
from app.models.bible import BibleVerse, BibleChapter, BibleBook
from app.schemas.bible_engagement import BookmarkCreate, ReadingPositionSet, ReadingCompletionCreate


class BookmarkService:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: uuid.UUID) -> list[tuple[Bookmark, BibleVerse, BibleChapter, BibleBook]]:
        return (
            self.db.query(Bookmark, BibleVerse, BibleChapter, BibleBook)
            .join(BibleVerse, BibleVerse.id == Bookmark.verse_id)
            .join(BibleChapter, BibleChapter.id == BibleVerse.chapter_id)
            .join(BibleBook, BibleBook.id == BibleChapter.book_id)
            .filter(Bookmark.user_id == user_id)
            .order_by(Bookmark.created_at.desc())
            .all()
        )

    def create(self, user_id: uuid.UUID, payload: BookmarkCreate) -> Bookmark:
        existing = (
            self.db.query(Bookmark)
            .filter(Bookmark.user_id == user_id, Bookmark.verse_id == payload.verse_id)
            .first()
        )
        if existing:
            return existing
        bookmark = Bookmark(user_id=user_id, verse_id=payload.verse_id, translation_id=payload.translation_id)
        self.db.add(bookmark)
        self.db.commit()
        self.db.refresh(bookmark)
        return bookmark

    def delete(self, user_id: uuid.UUID, bookmark_id: uuid.UUID) -> None:
        bookmark = self.db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
        if not bookmark:
            raise NotFoundError("Bookmark not found")
        if bookmark.user_id != user_id:
            raise ForbiddenError("You can only remove your own bookmarks")
        self.db.delete(bookmark)
        self.db.commit()

    def bookmarked_verse_ids(self, user_id: uuid.UUID, verse_ids: list[uuid.UUID]) -> set[uuid.UUID]:
        if not verse_ids:
            return set()
        rows = (
            self.db.query(Bookmark.verse_id)
            .filter(Bookmark.user_id == user_id, Bookmark.verse_id.in_(verse_ids))
            .all()
        )
        return {r[0] for r in rows}


class ReadingPositionService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: uuid.UUID) -> ReadingPosition | None:
        return self.db.query(ReadingPosition).filter(ReadingPosition.user_id == user_id).first()

    def set(self, user_id: uuid.UUID, payload: ReadingPositionSet) -> ReadingPosition:
        position = self.get(user_id)
        if position:
            position.translation_id = payload.translation_id
            position.book_id = payload.book_id
            position.chapter_number = payload.chapter_number
            position.verse_number = payload.verse_number
        else:
            position = ReadingPosition(
                user_id=user_id,
                translation_id=payload.translation_id,
                book_id=payload.book_id,
                chapter_number=payload.chapter_number,
                verse_number=payload.verse_number,
            )
            self.db.add(position)
        self.db.commit()
        self.db.refresh(position)
        return position


class ReadingCompletionService:
    def __init__(self, db: Session):
        self.db = db

    def mark_complete(self, user_id: uuid.UUID, payload: ReadingCompletionCreate):
        existing = (
            self.db.query(ReadingCompletion)
            .filter(
                ReadingCompletion.user_id == user_id,
                ReadingCompletion.translation_id == payload.translation_id,
                ReadingCompletion.book_id == payload.book_id,
                ReadingCompletion.chapter_number == payload.chapter_number,
            )
            .first()
        )
        if existing:
            return existing, True
        completion = ReadingCompletion(
            user_id=user_id,
            translation_id=payload.translation_id,
            book_id=payload.book_id,
            chapter_number=payload.chapter_number,
        )
        self.db.add(completion)
        self.db.commit()
        self.db.refresh(completion)
        return completion, False

    def completed_chapter_numbers(self, user_id: uuid.UUID, book_id: uuid.UUID) -> set[int]:
        rows = (
            self.db.query(ReadingCompletion.chapter_number)
            .filter(ReadingCompletion.user_id == user_id, ReadingCompletion.book_id == book_id)
            .all()
        )
        return {r[0] for r in rows}
