"""The single source of truth for "which organization does this ADMIN
manage" - see app/models/user.py's UserRole. A user's global role becomes
ADMIN only when Super Admin assigns them to manage exactly one Church OR
one Fellowship here; there is deliberately no way to be ADMIN of more than
one organization, and no way to be ADMIN without an assignment (enforced
by the unique constraints below, not just application code)."""
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class AdminOrganizationAssignment(Base):
    __tablename__ = "admin_organization_assignments"
    __table_args__ = (
        CheckConstraint("organization_type in ('church','fellowship')", name="chk_admin_assignment_org_type"),
        CheckConstraint(
            "(organization_type = 'church' and church_id is not null and fellowship_id is null) "
            "or (organization_type = 'fellowship' and fellowship_id is not null and church_id is null)",
            name="chk_admin_assignment_org_matches_id",
        ),
        # One admin per user (a user can manage exactly one organization)
        # and one admin per organization (each Church/Fellowship has
        # exactly one Admin at a time).
        UniqueConstraint("user_id", name="uq_admin_assignment_user"),
        UniqueConstraint("church_id", name="uq_admin_assignment_church"),
        UniqueConstraint("fellowship_id", name="uq_admin_assignment_fellowship"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_type: Mapped[str] = mapped_column(String(20), nullable=False)
    church_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("church.id", ondelete="CASCADE"), nullable=True)
    fellowship_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("fellowship.id", ondelete="CASCADE"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
