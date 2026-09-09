import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.repositories.bible_repository import BibleRepository
from app.schemas.bible_engagement import (
    BookmarkCreate,
    BookmarkOut,
    ReadingPositionSet,
    ReadingPositionOut,
    ReadingCompletionCreate,
    ReadingCompletionOut,
)
from app.services.bible_engagement_service import BookmarkService, ReadingPositionService, ReadingCompletionService

router = APIRouter(prefix="/bible", tags=["Bible Engagement"])


@router.get("/bookmarks", response_model=list[BookmarkOut], summary="List my bookmarks")
def list_bookmarks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = BookmarkService(db).list_for_user(current_user.id)
    return [
        BookmarkOut(
            id=bookmark.id,
            verse_id=bookmark.verse_id,
            translation_id=bookmark.translation_id,
            book_name=book.name,
            chapter_number=chapter.chapter_number,
            verse_number=verse.verse_number,
            verse_text=verse.text,
            created_at=bookmark.created_at,
        )
        for bookmark, verse, chapter, book in rows
    ]


@router.post("/bookmarks", response_model=BookmarkOut, summary="Bookmark a verse")
def create_bookmark(payload: BookmarkCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = BookmarkService(db)
    bookmark = service.create(current_user.id, payload)
    repo = BibleRepository(db)
    verse = repo.get_verse(bookmark.verse_id)
    return BookmarkOut(
        id=bookmark.id,
        verse_id=bookmark.verse_id,
        translation_id=bookmark.translation_id,
        book_name=verse.chapter.book.name,
        chapter_number=verse.chapter.chapter_number,
        verse_number=verse.verse_number,
        verse_text=verse.text,
        created_at=bookmark.created_at,
    )


@router.delete("/bookmarks/{bookmark_id}", summary="Remove my own bookmark")
def delete_bookmark(bookmark_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    BookmarkService(db).delete(current_user.id, bookmark_id)
    return {"success": True}


@router.get("/reading-position", response_model=ReadingPositionOut | None, summary="Where I last left off reading")
def get_reading_position(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    position = ReadingPositionService(db).get(current_user.id)
    if not position:
        return None
    return ReadingPositionOut(
        translation_code=position.translation.code,
        book_name=position.book.name,
        chapter_number=position.chapter_number,
        verse_number=position.verse_number,
        updated_at=position.updated_at,
    )


@router.put("/reading-position", response_model=ReadingPositionOut, summary="Save my current reading position")
def set_reading_position(payload: ReadingPositionSet, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    position = ReadingPositionService(db).set(current_user.id, payload)
    return ReadingPositionOut(
        translation_code=position.translation.code,
        book_name=position.book.name,
        chapter_number=position.chapter_number,
        verse_number=position.verse_number,
        updated_at=position.updated_at,
    )


@router.post("/reading-completion", response_model=ReadingCompletionOut, summary="Mark a chapter read (standalone, no plan required)")
def mark_chapter_complete(payload: ReadingCompletionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    completion, already_completed = ReadingCompletionService(db).mark_complete(current_user.id, payload)
    return ReadingCompletionOut(
        id=completion.id,
        translation_id=completion.translation_id,
        book_id=completion.book_id,
        chapter_number=completion.chapter_number,
        completed_at=completion.completed_at,
        already_completed=already_completed,
    )


@router.get("/reading-completion/{book_id}", response_model=list[int], summary="Which chapters of this book I've completed")
def completed_chapters_for_book(book_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return sorted(ReadingCompletionService(db).completed_chapter_numbers(current_user.id, book_id))
