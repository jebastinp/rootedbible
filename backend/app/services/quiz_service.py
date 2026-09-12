import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.models.quiz import QuizQuestion
from app.repositories.quiz_repository import QuizRepository
from app.repositories.bible_repository import BibleRepository
from app.services.progress_service import ProgressService
from app.services import audit_service
from app.schemas.quiz import (
    QuizForChapterOut,
    QuizQuestionOut,
    QuizSubmitRequest,
    QuizSubmitResponse,
    WrongAnswerHint,
    QuizQuestionAdminOut,
    QuizQuestionCreate,
    QuizQuestionUpdate,
)


class QuizService:
    """
    Implements plan section 6 (Completion Rule) and section 7 (Quiz Rules):
    reading isn't marked complete on a single click - it requires passing
    this quiz. Passing is intentionally forgiving (70%, not 100%) per the
    plan's instruction that "the quiz should encourage learning, not punish."
    """
    PASS_THRESHOLD = 0.7

    def __init__(self, db: Session, church_id: uuid.UUID | None = None, fellowship_id: uuid.UUID | None = None):
        self.db = db
        self.quiz_repo = QuizRepository(db)
        self.bible_repo = BibleRepository(db)
        self.progress_service = ProgressService(db)
        self.church_id = church_id
        self.fellowship_id = fellowship_id

    def get_quiz_for_chapter(self, chapter_id: uuid.UUID, age_group: str = "adult", user_id: uuid.UUID | None = None) -> QuizForChapterOut:
        """Draws from the member's chosen Church/Fellowship's own quiz bank
        for this chapter if they have one; falls back to the platform bank
        otherwise (same fallback rule as the reading calendar)."""
        church_id = fellowship_id = None
        if user_id is not None:
            from app.models.user import User
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                church_id, fellowship_id = user.active_calendar_church_id, user.active_calendar_fellowship_id

        questions = self.quiz_repo.get_questions_for_chapter(chapter_id, age_group, church_id, fellowship_id)
        if not questions and (church_id or fellowship_id):
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
        church_id = fellowship_id = None

        for answer in payload.answers:
            question = self.quiz_repo.get_question_by_id(answer.question_id)
            if not question:
                continue
            church_id, fellowship_id = question.church_id, question.fellowship_id
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
            church_id=church_id,
            fellowship_id=fellowship_id,
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

    # -----------------------------------------------------------------
    # Admin: quiz question management
    # -----------------------------------------------------------------
    def resolve_chapter_id(self, version_code: str, book_name: str, chapter_number: int) -> uuid.UUID:
        version = self.bible_repo.get_version_by_code(version_code)
        if not version:
            raise NotFoundError(f"Bible version '{version_code}' not found")
        book = self.bible_repo.get_book_by_name(version.id, book_name)
        if not book:
            raise NotFoundError(f"Book '{book_name}' not found in {version.version_name}")
        chapter = self.bible_repo.get_chapter(book.id, chapter_number)
        if not chapter:
            raise NotFoundError(f"{book_name} {chapter_number} not found in {version.version_name}")
        return chapter.id

    def _validate_correct_index(self, options: list[str], correct_index: int) -> None:
        if correct_index >= len(options):
            raise ValidationError("correct_index must point at one of the given options.")

    def admin_list_questions_for_chapter(self, chapter_id: uuid.UUID) -> list[QuizQuestionAdminOut]:
        return [QuizQuestionAdminOut.model_validate(q) for q in self.quiz_repo.list_all_for_chapter(chapter_id, self.church_id, self.fellowship_id)]

    def admin_create_question(self, actor_id: uuid.UUID, chapter_id: uuid.UUID, payload: QuizQuestionCreate) -> QuizQuestionAdminOut:
        self._validate_correct_index(payload.options, payload.correct_index)
        question = QuizQuestion(
            chapter_id=chapter_id, church_id=self.church_id, fellowship_id=self.fellowship_id,
            question=payload.question, options=payload.options,
            correct_index=payload.correct_index, verse_reference=payload.verse_reference, age_group=payload.age_group,
        )
        self.db.add(question)
        self.db.flush()
        audit_service.record(self.db, actor_id, "quiz_question_created", "quiz_question", question.id, {"chapter_id": str(chapter_id)})
        self.db.commit()
        self.db.refresh(question)
        return QuizQuestionAdminOut.model_validate(question)

    def _get_question(self, question_id: uuid.UUID) -> QuizQuestion:
        question = self.quiz_repo.get_question_by_id(question_id)
        if not question or question.church_id != self.church_id or question.fellowship_id != self.fellowship_id:
            raise NotFoundError("Quiz question not found.")
        return question

    def admin_update_question(self, actor_id: uuid.UUID, question_id: uuid.UUID, payload: QuizQuestionUpdate) -> QuizQuestionAdminOut:
        question = self._get_question(question_id)
        changes = payload.model_dump(exclude_unset=True)
        options = changes.get("options", question.options)
        correct_index = changes.get("correct_index", question.correct_index)
        self._validate_correct_index(options, correct_index)
        for field, value in changes.items():
            setattr(question, field, value)
        audit_service.record(self.db, actor_id, "quiz_question_updated", "quiz_question", question.id)
        self.db.commit()
        self.db.refresh(question)
        return QuizQuestionAdminOut.model_validate(question)

    def admin_delete_question(self, actor_id: uuid.UUID, question_id: uuid.UUID) -> None:
        question = self._get_question(question_id)
        audit_service.record(self.db, actor_id, "quiz_question_deleted", "quiz_question", question.id)
        self.db.delete(question)
        self.db.commit()
