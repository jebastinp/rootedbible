import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Text, Boolean, ForeignKey, UniqueConstraint, func, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class BibleVersion(Base):
    """
    One row per translation. `license_status` exists so the app can be
    honest about what's legally cleared:
      - "public_domain": a legacy classification, not proof of release rights.
      - "pending": listed but not yet licensed - hidden from users until
        an admin flips it to "licensed" (e.g. NKJV, Tamil/Telugu/Kannada/Hindi
        versions once the church has written permission).
      - "licensed": cleared and visible.
    Never flip a version to "licensed" without an actual signed agreement.
    All content lookup also requires the reviewed external licensing registry.
    """
    __tablename__ = "bible_version"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # e.g. "kjv1769", "nkjv", "ta_bsi"
    language: Mapped[str] = mapped_column(String(40), nullable=False)  # "English", "Tamil", ...
    version_name: Mapped[str] = mapped_column(String(120), nullable=False)  # "King James Version (1769)"
    license_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    books: Mapped[list["BibleBook"]] = relationship(back_populates="version", cascade="all, delete-orphan")


class BibleBook(Base):
    __tablename__ = "bible_book"
    __table_args__ = (UniqueConstraint("bible_version_id", "name", name="uq_book_per_version"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bible_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bible_version.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(60), nullable=False)  # "Genesis", "John", ...
    testament: Mapped[str] = mapped_column(String(3), nullable=False)  # "OT" or "NT"
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..66, canonical order
    chapter_count: Mapped[int] = mapped_column(Integer, nullable=False)

    version: Mapped["BibleVersion"] = relationship(back_populates="books")
    chapters: Mapped[list["BibleChapter"]] = relationship(back_populates="book", cascade="all, delete-orphan")


class BibleChapter(Base):
    __tablename__ = "bible_chapter"
    __table_args__ = (UniqueConstraint("book_id", "chapter_number", name="uq_chapter_per_book"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bible_book.id", ondelete="CASCADE"), nullable=False)
    chapter_number: Mapped[int] = mapped_column(Integer, nullable=False)

    book: Mapped["BibleBook"] = relationship(back_populates="chapters")
    verses: Mapped[list["BibleVerse"]] = relationship(back_populates="chapter", cascade="all, delete-orphan", order_by="BibleVerse.verse_number")
    quiz_questions: Mapped[list["QuizQuestion"]] = relationship(back_populates="chapter", cascade="all, delete-orphan")


class BibleVerse(Base):
    """Each verse is individually addressable so highlights/notes/bookmarks
    can reference a stable verse_id instead of matching on text - different
    translations of 'the same' verse have different text, so text can never
    be the identity."""
    __tablename__ = "bible_verse"
    __table_args__ = (UniqueConstraint("chapter_id", "verse_number", name="uq_verse_per_chapter"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bible_chapter.id", ondelete="CASCADE"), nullable=False)
    verse_number: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    chapter: Mapped["BibleChapter"] = relationship(back_populates="verses")
