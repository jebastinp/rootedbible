from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.bible import BibleVersionOut, BibleBookOut, BibleChapterOut, ChapterNav, SearchResponseOut
from app.services.bible_content_service import BibleContentService

router = APIRouter(prefix="/bible", tags=["Bible Content"])


@router.get("/versions", response_model=list[BibleVersionOut], summary="List Bible versions visible to users")
def list_versions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return BibleContentService(db).list_versions()


@router.get("/versions/{version_code}/books", response_model=list[BibleBookOut], summary="List books in a version")
def list_books(version_code: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return BibleContentService(db).list_books(version_code)


@router.get(
    "/versions/{version_code}/{book_name}/{chapter_number}",
    response_model=BibleChapterOut,
    summary="Get a single chapter's text",
)
def get_chapter(
    version_code: str,
    book_name: str,
    chapter_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return BibleContentService(db).get_chapter(version_code, book_name, chapter_number)


@router.get(
    "/versions/{version_code}/{book_name}/{chapter_number}/nav",
    response_model=ChapterNav,
    summary="Previous/next chapter for reading-screen navigation",
)
def get_navigation(
    version_code: str,
    book_name: str,
    chapter_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return BibleContentService(db).get_navigation(version_code, book_name, chapter_number)


@router.get(
    "/versions/{version_code}/search",
    response_model=SearchResponseOut,
    summary="Search Scripture text, or jump straight to a reference like 'John 3:16'",
)
def search(
    version_code: str,
    q: str = Query(..., min_length=1, max_length=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return BibleContentService(db).search(version_code, q)
