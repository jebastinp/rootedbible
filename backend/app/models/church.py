"""Church is a standalone community entity - independent of Church
Challenge (which is a time-bound reading challenge a church can run, not
the church itself). A user requests to join; the church's admin approves,
exactly like every other Rooted membership."""
import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class CommunityPrivacy(str, enum.Enum):
    public = "public"
    private = "private"
    invite_only = "invite_only"


class ChurchStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"


class Church(Base):
    __tablename__ = "church"
    __table_args__ = (
        CheckConstraint("status in ('active','suspended')", name="chk_church_status"),
        CheckConstraint("privacy in ('public','private','invite_only')", name="chk_church_privacy"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    church_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    privacy: Mapped[str] = mapped_column(String(20), nullable=False, default=CommunityPrivacy.public.value)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=ChurchStatus.active.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ChurchMember(Base):
    __tablename__ = "church_member"
    __table_args__ = (
        UniqueConstraint("church_id", "user_id", name="uq_church_member_once"),
        CheckConstraint("role in ('owner','admin','member')", name="chk_church_member_role"),
        CheckConstraint("status in ('active','removed','left')", name="chk_church_member_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    church_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("church.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(10), nullable=False, default="member")
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="active")
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
