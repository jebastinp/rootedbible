"""Fellowship - a standalone community entity, same request/approval
membership pattern as Church/Family/Buddy. Optionally scoped to a Church
(a church's small-group fellowships) but can also stand alone."""
import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Fellowship(Base):
    __tablename__ = "fellowship"
    __table_args__ = (
        CheckConstraint("status in ('active','suspended')", name="chk_fellowship_status"),
        CheckConstraint("privacy in ('public','private','invite_only')", name="chk_fellowship_privacy"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    fellowship_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    church_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("church.id", ondelete="SET NULL"), nullable=True)
    # Legacy display field only - see Church.owner_id.
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    privacy: Mapped[str] = mapped_column(String(20), nullable=False, default="public")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FellowshipMember(Base):
    __tablename__ = "fellowship_member"
    __table_args__ = (
        UniqueConstraint("fellowship_id", "user_id", name="uq_fellowship_member_once"),
        CheckConstraint("role in ('owner','admin','member')", name="chk_fellowship_member_role"),
        CheckConstraint("status in ('active','removed','left')", name="chk_fellowship_member_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fellowship_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fellowship.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(10), nullable=False, default="member")
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="active")
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
