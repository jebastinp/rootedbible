import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ConflictError
from app.repositories.quiz_repository import QuizRepository
from app.services.progress_service import ProgressService
from app.schemas.quiz import (
    QuizForChapterOut,
    QuizQuestionOut,
    QuizSubmitRequest,
    QuizSubmitResponse,
    WrongAnswerHint,
)


class QuizService:
    """
    Implements plan section 6 (Completion Rule) and section 7 (Quiz Rules):
    reading isn't marked complete on a single click - it requires passing
    this quiz. Passing is intentionally forgiving (70%, not 100%) per the
    plan's instruction that "the quiz should encourage learning, not punish."
    """
    PASS_THRESHOLD = 0.7

    def __init__(self, db: Session):
        self.db = db
        self.quiz_repo = QuizRepository(db)
        self.progress_service = ProgressService(db)

    def get_quiz_for_chapter(self, chapter_id: uuid.UUID, age_group: str = "adult") -> QuizForChapterOut:
        questions = self.quiz_repo.get_questions_for_chapter(chapter_id, age_group)
        if not questions:
            raise NotFoundError("No quiz questions have been written for this chapter yet.")
        return QuizForChapterOut(
            chapter_id=chapter_id,
            questions=[QuizQuestionOut.model_validate(q) for q in questions],
        )

    def submit_attempt(self, user_id: uuid.UUID, payload: QuizSubmitRequest) -> QuizSubmitResponse:
        score = 0
        hints: list[WrongAnswerHint] = []

        for answer in payload.answers:
            question = self.quiz_repo.get_question_by_id(answer.question_id)
            if not question:
                continue
            if answer.selected_index == question.correct_index:
                score += 1
            else:
                # Verse hint, not the answer itself - the plan calls for
                # nudging the reader back to the text, not just revealing it.
                hints.append(WrongAnswerHint(question_id=question.id, verse_reference=question.verse_reference))

        total = len(payload.answers)
        passed = total > 0 and (score / total) >= self.PASS_THRESHOLD
        attempt_count = self.quiz_repo.count_previous_attempts(user_id, payload.reading_plan_id) + 1

        self.quiz_repo.create_attempt(
            user_id=user_id,
            reading_plan_id=payload.reading_plan_id,
            chapter_id=payload.chapter_id,
            score=score,
            total_questions=total,
            passed=passed,
            attempt_count=attempt_count,
        )

        if passed:
            # Only actually flips "completed" if reading_plan_id is today's
            # plan - passing a quiz for a catch-up/past day still records
            # the attempt (and points), it just doesn't touch the streak.
            try:
                self.progress_service.mark_today_completed(user_id)
            except (NotFoundError, ConflictError):
                pass

        return QuizSubmitResponse(
            score=score,
            total_questions=total,
            passed=passed,
            attempt_count=attempt_count,
            hints=[] if passed else hints,
        )
