import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class RootedIdLookupOut(BaseModel):
    """Minimal identity only - never email, never private data."""
    user_id: str
    name: str
    photo_url: Optional[str] = None


# ---------------------------------------------------------------------
# Church Challenge - admin
# ---------------------------------------------------------------------
class ChallengeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    church_name: str = Field(min_length=2, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    reading_plan_id: Optional[uuid.UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    # None = unlimited, no default cap. If set, must be at least 2.
    participant_limit: Optional[int] = Field(default=None, ge=2, le=1000000)
    allow_families: bool = True
    allow_buddies: bool = True
    quiz_enabled: bool = True
    rewards_enabled: bool = True
    status: str = Field(default="draft", pattern="^(draft|active|completed|archived)$")


class ChallengeUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    church_name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    reading_plan_id: Optional[uuid.UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    participant_limit: Optional[int] = Field(default=None, ge=2, le=1000000)
    allow_families: Optional[bool] = None
    allow_buddies: Optional[bool] = None
    quiz_enabled: Optional[bool] = None
    rewards_enabled: Optional[bool] = None
    status: Optional[str] = Field(default=None, pattern="^(draft|active|completed|archived)$")


class ChallengeAdminOut(BaseModel):
    id: uuid.UUID
    name: str
    church_name: str
    description: Optional[str] = None
    reading_plan_id: Optional[uuid.UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    participant_limit: Optional[int] = None
    participant_count: int
    status: str
    allow_families: bool
    allow_buddies: bool
    quiz_enabled: bool
    rewards_enabled: bool
    created_at: datetime


# ---------------------------------------------------------------------
# Church Challenge - user-facing
# ---------------------------------------------------------------------
class ChallengeSummaryOut(BaseModel):
    id: uuid.UUID
    name: str
    church_name: str
    status: str
    day_number: Optional[int] = None
    total_days: Optional[int] = None
    my_progress_percent: int
    my_status: str  # "pending" | "active"
    has_family: bool
    has_buddy_group: bool


class TodayReadingOut(BaseModel):
    old_testament: Optional[str] = None
    new_testament: Optional[str] = None
    estimated_minutes: Optional[int] = None
    completed: bool


class ChallengeGroupSummary(BaseModel):
    id: uuid.UUID
    name: str
    member_count: int
    max_members: Optional[int] = None  # None = no cap
    completed_today_count: int


class ChallengeDetailOut(BaseModel):
    id: uuid.UUID
    name: str
    church_name: str
    description: Optional[str] = None
    status: str
    day_number: Optional[int] = None
    total_days: Optional[int] = None
    my_progress_percent: int
    my_streak: int
    my_status: str
    today: Optional[TodayReadingOut] = None
    family: Optional[ChallengeGroupSummary] = None
    buddy_group: Optional[ChallengeGroupSummary] = None
    quiz_enabled: bool
    rewards_enabled: bool
    participant_count: int
    participant_limit: Optional[int] = None


# ---------------------------------------------------------------------
# Family / Buddy groups
# ---------------------------------------------------------------------
class GroupCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)


class GroupMemberOut(BaseModel):
    user_id: str
    name: str
    photo_url: Optional[str] = None
    role: str
    completed_today: bool
    current_streak: int


class GroupDetailOut(BaseModel):
    id: uuid.UUID
    challenge_id: Optional[uuid.UUID] = None
    name: str
    description: Optional[str] = None
    my_role: str
    max_members: Optional[int] = None  # None = no cap
    members: list[GroupMemberOut]


class InviteByRootedId(BaseModel):
    rooted_id: str = Field(min_length=1, max_length=20)


class GroupAdminSummaryOut(BaseModel):
    """Super Admin's platform-wide view of every Family/Buddy Group -
    private groups are never visible to other normal users, but are always
    visible here for moderation/support."""
    id: uuid.UUID
    name: str
    owner_user_id: str
    owner_name: str
    member_count: int
    challenge_id: Optional[uuid.UUID] = None
    challenge_name: Optional[str] = None
    privacy: str
    created_at: datetime


# ---------------------------------------------------------------------
# Admin: challenge members / pending requests
# ---------------------------------------------------------------------
class ChallengeMemberAdminOut(BaseModel):
    user_id: str
    name: str
    family_name: Optional[str] = None
    buddy_group_name: Optional[str] = None
    progress_percent: int
    streak: int
    completed_today: bool
    status: str


class ChallengeRequestAdminOut(BaseModel):
    request_id: uuid.UUID
    user_id: str
    name: str
    requested_at: datetime


# ---------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------
class JoinRequestOut(BaseModel):
    id: uuid.UUID
    type: str  # challenge | family | buddy
    direction: str  # incoming | outgoing
    challenge_id: Optional[uuid.UUID] = None
    family_id: Optional[uuid.UUID] = None
    buddy_group_id: Optional[uuid.UUID] = None
    scope_name: str
    other_party_user_id: Optional[str] = None
    other_party_name: Optional[str] = None
    status: str
    created_at: datetime


# ---------------------------------------------------------------------
# Rewards
# ---------------------------------------------------------------------
class RewardCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    requirement_type: str = Field(pattern="^(streak|completion)$")
    requirement_value: int = Field(ge=1)
    badge_icon: Optional[str] = Field(default=None, max_length=40)


class RewardOut(BaseModel):
    id: uuid.UUID
    challenge_id: uuid.UUID
    name: str
    description: Optional[str] = None
    requirement_type: str
    requirement_value: int
    badge_icon: Optional[str] = None


class RewardEarnedOut(RewardOut):
    earned: bool


# ---------------------------------------------------------------------
# Encouragement
# ---------------------------------------------------------------------
class EncouragementCreate(BaseModel):
    message: str = Field(min_length=1, max_length=120)
    to_user_id: Optional[str] = None  # Rooted ID, buddy-only "encourage this person"


# ---------------------------------------------------------------------
# Leaderboard
# ---------------------------------------------------------------------
class LeaderboardConfigOut(BaseModel):
    scope: str  # individual | family | buddy | <RootedGroup name>
    label: str
    ranking_limit: int


class LeaderboardConfigUpdate(BaseModel):
    ranking_limit: int = Field(ge=1, le=100)


class LeaderboardEntryOut(BaseModel):
    rank: int
    entry_id: str  # rooted_id for individual, group/entity uuid otherwise
    name: str
    progress_percent: int


class LeaderboardOut(BaseModel):
    scope: str
    label: str
    ranking_limit: int
    entries: list[LeaderboardEntryOut]
