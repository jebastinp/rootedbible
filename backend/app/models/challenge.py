"""Church Challenge is the parent container for Rooted's community system.

There is no global community. A Family or Buddy Group always belongs to
exactly one Church Challenge, and only users who are ACTIVE participants of
that challenge can belong to its Family/Buddy groups. Membership is never
automatic - every relationship (challenge, family, buddy) passes through a
JoinRequest that must be approved before it becomes active.
"""
import enum
import uuid
from datetime import date, datetime

from sqlalchemy import String, Text, Integer, Boolean, Date, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class ChallengeStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    completed = "completed"
    archived = "archived"


class ChallengeMemberStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    removed = "removed"


class GroupMemberRole(str, enum.Enum):
    owner = "owner"
    member = "member"


class GroupMemberStatus(str, enum.Enum):
    active = "active"
    removed = "removed"
    left = "left"


class RequestType(str, enum.Enum):
    challenge = "challenge"
    family = "family"
    buddy = "buddy"


class RequestStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    declined = "declined"
    cancelled = "cancelled"


class ChurchChallenge(Base):
    __tablename__ = "church_challenge"
    __table_args__ = (
        CheckConstraint("status in ('draft','active','completed','archived')", name="chk_challenge_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    church_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    reading_plan_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("reading_plan.id", ondelete="SET NULL"), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    participant_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=ChallengeStatus.draft.value)
    allow_families: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    family_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    allow_buddies: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    buddy_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    quiz_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    rewards_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ChallengeMember(Base):
    __tablename__ = "challenge_member"
    __table_args__ = (
        UniqueConstraint("challenge_id", "user_id", name="uq_challenge_member_once"),
        CheckConstraint("status in ('pending','active','removed')", name="chk_challenge_member_status"),
        CheckConstraint("role in ('participant','admin')", name="chk_challenge_member_role"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("church_challenge.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=ChallengeMemberStatus.pending.value)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="participant")
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Family(Base):
    __tablename__ = "family"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("church_challenge.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FamilyMember(Base):
    __tablename__ = "family_member"
    __table_args__ = (
        UniqueConstraint("family_id", "user_id", name="uq_family_member_once"),
        CheckConstraint("role in ('owner','member')", name="chk_family_member_role"),
        CheckConstraint("status in ('active','removed','left')", name="chk_family_member_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(10), nullable=False, default=GroupMemberRole.member.value)
    status: Mapped[str] = mapped_column(String(10), nullable=False, default=GroupMemberStatus.active.value)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BuddyGroup(Base):
    __tablename__ = "buddy_group"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("church_challenge.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class BuddyMember(Base):
    __tablename__ = "buddy_member"
    __table_args__ = (
        UniqueConstraint("buddy_group_id", "user_id", name="uq_buddy_member_once"),
        CheckConstraint("role in ('owner','member')", name="chk_buddy_member_role"),
        CheckConstraint("status in ('active','removed','left')", name="chk_buddy_member_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buddy_group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("buddy_group.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(10), nullable=False, default=GroupMemberRole.member.value)
    status: Mapped[str] = mapped_column(String(10), nullable=False, default=GroupMemberStatus.active.value)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class JoinRequest(Base):
    """One model for all three request types. Never confuse a request with
    membership - a row here only becomes a ChallengeMember/FamilyMember/
    BuddyMember once `status` is 'approved'."""
    __tablename__ = "join_request"
    __table_args__ = (
        CheckConstraint("type in ('challenge','family','buddy')", name="chk_request_type"),
        CheckConstraint("status in ('pending','approved','declined','cancelled')", name="chk_request_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    requester_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    challenge_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("church_challenge.id", ondelete="CASCADE"), nullable=True)
    family_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("family.id", ondelete="CASCADE"), nullable=True)
    buddy_group_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("buddy_group.id", ondelete="CASCADE"), nullable=True)
    status: Mapped[str] = mapped_column(String(10), nullable=False, default=RequestStatus.pending.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    responded_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)


class ChallengeReward(Base):
    __tablename__ = "challenge_reward"
    __table_args__ = (
        CheckConstraint("requirement_type in ('streak','completion')", name="chk_reward_requirement_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("church_challenge.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    requirement_type: Mapped[str] = mapped_column(String(20), nullable=False)
    requirement_value: Mapped[int] = mapped_column(Integer, nullable=False)
    badge_icon: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Encouragement(Base):
    """Predefined-message encouragement only - deliberately not a social
    feed. Exactly one of family_id / buddy_group_id is set."""
    __tablename__ = "encouragement"
    __table_args__ = (
        CheckConstraint(
            "(family_id is not null and buddy_group_id is null) or (family_id is null and buddy_group_id is not null)",
            name="chk_encouragement_one_scope",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    to_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    family_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("family.id", ondelete="CASCADE"), nullable=True)
    buddy_group_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("buddy_group.id", ondelete="CASCADE"), nullable=True)
    message: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
