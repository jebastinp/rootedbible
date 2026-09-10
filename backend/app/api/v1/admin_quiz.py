import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_admin
from app.models.user import User
from app.schemas.quiz import QuizQuestionAdminOut, QuizQuestionCreate, QuizQuestionUpdate
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/admin/quiz", tags=["Admin - Quiz"])


@router.get("/chapter", response_model=list[QuizQuestionAdminOut], summary="List quiz questions for a chapter (identify by version/book/chapter)")
def list_questions(
    version_code: str = Query(...),
    book_name: str = Query(...),
    chapter_number: int = Query(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = QuizService(db)
    chapter_id = service.resolve_chapter_id(version_code, book_name, chapter_number)
    return service.admin_list_questions_for_chapter(chapter_id)


@router.post("/chapter", response_model=QuizQuestionAdminOut, summary="Add a quiz question to a chapter")
def create_question(
    payload: QuizQuestionCreate,
    version_code: str = Query(...),
    book_name: str = Query(...),
    chapter_number: int = Query(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = QuizService(db)
    chapter_id = service.resolve_chapter_id(version_code, book_name, chapter_number)
    return service.admin_create_question(current_user.id, chapter_id, payload)


@router.patch("/{question_id}", response_model=QuizQuestionAdminOut, summary="Update a quiz question")
def update_question(question_id: uuid.UUID, payload: QuizQuestionUpdate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return QuizService(db).admin_update_question(current_user.id, question_id, payload)


@router.delete("/{question_id}", summary="Delete a quiz question")
def delete_question(question_id: uuid.UUID, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    QuizService(db).admin_delete_question(current_user.id, question_id)
    return {"success": True}
