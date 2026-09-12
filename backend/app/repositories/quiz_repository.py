import uuid

from sqlalchemy.orm import Session

from app.models.quiz import QuizQuestion, QuizAttempt


class QuizRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_questions_for_chapter(self, chapter_id: uuid.UUID, age_group: str = "adult", church_id: uuid.UUID | None = None, fellowship_id: uuid.UUID | None = None) -> list[QuizQuestion]:
        return (
            self.db.query(QuizQuestion)
            .filter(
                QuizQuestion.chapter_id == chapter_id, QuizQuestion.age_group == age_group,
                QuizQuestion.church_id == church_id, QuizQuestion.fellowship_id == fellowship_id,
            )
            .all()
        )

    def get_question_by_id(self, question_id: uuid.UUID) -> QuizQuestion | None:
        return self.db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()

    def count_previous_attempts(self, user_id: uuid.UUID, reading_plan_id: uuid.UUID) -> int:
        return (
            self.db.query(QuizAttempt)
            .filter(QuizAttempt.user_id == user_id, QuizAttempt.reading_plan_id == reading_plan_id)
            .count()
        )

    def create_attempt(self, **kwargs) -> QuizAttempt:
        attempt = QuizAttempt(**kwargs)
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def list_all_for_chapter(self, chapter_id: uuid.UUID, church_id: uuid.UUID | None = None, fellowship_id: uuid.UUID | None = None) -> list[QuizQuestion]:
        return (
            self.db.query(QuizQuestion)
            .filter(QuizQuestion.chapter_id == chapter_id, QuizQuestion.church_id == church_id, QuizQuestion.fellowship_id == fellowship_id)
            .order_by(QuizQuestion.age_group)
            .all()
        )

    def has_passed(self, user_id: uuid.UUID, reading_plan_id: uuid.UUID) -> bool:
        return (
            self.db.query(QuizAttempt)
            .filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.reading_plan_id == reading_plan_id,
                QuizAttempt.passed.is_(True),
            )
            .first()
            is not None
        )
