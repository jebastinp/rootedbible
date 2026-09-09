import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Text, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class QuizQuestion(Base):
    __tablename__ = "quiz_question"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bible_chapter.id", ondelete="CASCADE"), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list] = mapped_column(JSONB, nullable=False)  # ["Option A", "Option B", ...]
    correct_index: Mapped[int] = mapped_column(Integer, nullable=False)  # index into options
    verse_reference: Mapped[str] = mapped_column(String(60), nullable=False)  # shown as a hint after a wrong answer
    age_group: Mapped[str] = mapped_column(String(10), nullable=False, default="adult")  # adult | 13-17 | 9-12 | 6-8 | 3-5

    chapter: Mapped["BibleChapter"] = relationship(back_populates="quiz_questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempt"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reading_plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reading_plan.id", ondelete="CASCADE"), nullable=False)
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("bible_chapter.id", ondelete="SET NULL"), nullable=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # correct answers this attempt
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # which retry this is
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
