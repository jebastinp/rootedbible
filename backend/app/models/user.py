import enum
import uuid
from datetime import date, datetime

from sqlalchemy import String, Enum, Date, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class UserRole(str, enum.Enum):
    """Exactly 3 roles, no others. `admin` is always organization-scoped -
    see AdminOrganizationAssignment for which Church or Fellowship a given
    admin manages. It is never platform-wide; that's `super_admin` alone."""
    member = "member"
    admin = "admin"
    super_admin = "super_admin"


class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "not (active_calendar_church_id is not null and active_calendar_fellowship_id is not null)",
            name="chk_user_one_active_calendar",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    supabase_user_id: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), default=UserRole.member, nullable=False)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus, name="user_status"), default=UserStatus.active, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String, nullable=True)
    joined_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    auth_provider: Mapped[str | None] = mapped_column(String(20), nullable=True)  # "google" | "email" | "legacy"
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Address - optional (collected at signup, editable later; not required
    # for the app to function, so nullable rather than blocking sign-up).
    house_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    street_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    city_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postcode: Mapped[str | None] = mapped_column(String(20), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Which org's own reading calendar/quiz bank this member follows -
    # both null = the shared platform default. At most one may be set;
    # the member explicitly chooses this in Settings when they belong to
    # more than one org that runs its own calendar.
    active_calendar_church_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("church.id", ondelete="SET NULL"), nullable=True)
    active_calendar_fellowship_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("fellowship.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    progress: Mapped[list["ReadingProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    stats: Mapped["UserStats"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")

    @property
    def is_staff(self) -> bool:
        """Platform-wide staff - Super Admin only. An `admin` is scoped to
        a single organization and is never platform staff (see
        AdminOrganizationAssignment)."""
        return self.role == UserRole.super_admin
