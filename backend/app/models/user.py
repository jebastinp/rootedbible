import enum
import uuid
from datetime import date, datetime

from sqlalchemy import String, Enum, Date, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class UserRole(str, enum.Enum):
    member = "member"
    leader = "leader"
    admin = "admin"
    super_admin = "super_admin"


class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class User(Base):
    __tablename__ = "users"

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

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    progress: Mapped[list["ReadingProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    stats: Mapped["UserStats"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")

    @property
    def is_staff(self) -> bool:
        return self.role in (UserRole.admin, UserRole.super_admin)
