import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.quiz import QuizForChapterOut, QuizSubmitRequest, QuizSubmitResponse
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.get(
    "/chapter/{chapter_id}",
    response_model=QuizForChapterOut,
    summary="Get quiz questions for a chapter (no answers included)",
)
def get_quiz(
    chapter_id: uuid.UUID,
    age_group: str = "adult",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return QuizService(db).get_quiz_for_chapter(chapter_id, age_group, user_id=current_user.id)


@router.post("/attempt", response_model=QuizSubmitResponse, summary="Submit quiz answers, allow retry")
def submit_attempt(
    payload: QuizSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return QuizService(db).submit_attempt(current_user.id, payload)
