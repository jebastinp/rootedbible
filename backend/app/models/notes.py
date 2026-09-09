import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Note(Base):
    __tablename__ = "note"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    verse_reference: Mapped[str] = mapped_column(String(60), nullable=False)  # e.g. "John 3:16" - for display only
    # Structured identity - never identify a verse solely by its (translation-specific) text.
    verse_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("bible_verse.id", ondelete="CASCADE"), nullable=True)
    translation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("bible_version.id", ondelete="CASCADE"), nullable=True)
    note_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Highlight(Base):
    __tablename__ = "highlight"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    verse_reference: Mapped[str] = mapped_column(String(60), nullable=False)
    color: Mapped[str] = mapped_column(String(10), nullable=False, default="yellow")  # yellow|blue|green|red|purple
    # Structured range identity - supports highlighting a span (e.g. John 3:16-18)
    # via the first verse's id plus how many consecutive verses it covers.
    verse_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("bible_verse.id", ondelete="CASCADE"), nullable=True)
    translation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("bible_version.id", ondelete="CASCADE"), nullable=True)
    verse_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    verse_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
