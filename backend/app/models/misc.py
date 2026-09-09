import enum
import uuid
from datetime import date, datetime

from sqlalchemy import String, Text, Date, DateTime, Boolean, Integer, Enum, ForeignKey, func, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class AnnouncementVisibility(str, enum.Enum):
    all = "all"
    members = "members"
    leaders = "leaders"
    admins = "admins"


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    publish_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    visibility: Mapped[AnnouncementVisibility] = mapped_column(
        Enum(AnnouncementVisibility, name="announcement_visibility"), default=AnnouncementVisibility.all, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ChurchSettings(Base):
    __tablename__ = "church_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    church_name: Mapped[str] = mapped_column(String(200), default="Rooted Church", nullable=False)
    church_logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    reading_year: Mapped[int] = mapped_column(Integer, default=2026, nullable=False)
    verse_of_the_day: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    log_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ImportStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    success = "success"
    failed = "failed"
    rolled_back = "rolled_back"


class ImportHistory(Base):
    __tablename__ = "import_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_type: Mapped[str] = mapped_column(String(30), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ImportStatus] = mapped_column(Enum(ImportStatus, name="import_status"), default=ImportStatus.pending, nullable=False)
    total_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    inserted_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skipped_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_log: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    imported_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
