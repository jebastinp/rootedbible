import uuid
from datetime import date, datetime

from sqlalchemy import String, Integer, Date, DateTime, Text, func, CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class ReadingPlan(Base):
    __tablename__ = "reading_plan"
    __table_args__ = (CheckConstraint("day_number > 0", name="chk_day_number_positive"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    day_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    reading_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False)
    old_testament: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_testament: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    progress_entries: Mapped[list["ReadingProgress"]] = relationship(back_populates="reading_plan", cascade="all, delete-orphan")
    passages: Mapped[list["ReadingPlanPassage"]] = relationship(
        back_populates="reading_plan", cascade="all, delete-orphan", order_by="ReadingPlanPassage.sort_order"
    )


class ReadingPlanPassage(Base):
    """
    Structured, validated Bible reference for one plan day - e.g. "Genesis 1-3"
    becomes {testament: OT, book_name: Genesis, chapter_start: 1, chapter_end: 3}.
    Exists so the app can deep-link straight into the Bible reader instead of
    regex-guessing a reference out of free text. book_name is canonical (matches
    bible_book.name) and independent of translation, since the same day's
    reading maps to different bible_book rows per translation.
    """
    __tablename__ = "reading_plan_passage"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reading_plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reading_plan.id", ondelete="CASCADE"), nullable=False)
    testament: Mapped[str] = mapped_column(String(3), nullable=False)  # "OT" or "NT"
    book_name: Mapped[str] = mapped_column(String(60), nullable=False)
    chapter_start: Mapped[int] = mapped_column(Integer, nullable=False)
    chapter_end: Mapped[int] = mapped_column(Integer, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    reading_plan: Mapped["ReadingPlan"] = relationship(back_populates="passages")
