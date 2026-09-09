"""User engagement with Scripture: bookmarks, reading position, and
standalone chapter completion (independent of any reading plan - the Bible
reader must work whether or not the user is following a plan)."""
import uuid
from datetime import datetime

from sqlalchemy import Integer, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Bookmark(Base):
    __tablename__ = "bookmark"
    __table_args__ = (UniqueConstraint("user_id", "verse_id", name="uq_bookmark_user_verse"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    verse_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bible_verse.id", ondelete="CASCADE"), nullable=False)
    translation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bible_version.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ReadingPosition(Base):
    """One row per user - 'Continue Reading' always reflects the single
    latest position, regardless of translation switches."""
    __tablename__ = "reading_position"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    translation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bible_version.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bible_book.id", ondelete="CASCADE"), nullable=False)
    chapter_number: Mapped[int] = mapped_column(Integer, nullable=False)
    verse_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    translation: Mapped["BibleVersion"] = relationship()
    book: Mapped["BibleBook"] = relationship()


class ReadingCompletion(Base):
    """Standalone chapter completion, separate from reading-plan day
    completion (ReadingProgress) - the Bible reader must work for a user
    who isn't following any plan at all."""
    __tablename__ = "reading_completion"
    __table_args__ = (UniqueConstraint("user_id", "translation_id", "book_id", "chapter_number", name="uq_completion_once"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    translation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bible_version.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bible_book.id", ondelete="CASCADE"), nullable=False)
    chapter_number: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
