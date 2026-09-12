import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------
# Church
# ---------------------------------------------------------------------
class ChurchCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    address: Optional[str] = Field(default=None, max_length=500)
    privacy: str = Field(default="public", pattern="^(public|private|invite_only)$")
    # If given, this Rooted ID becomes the church's owner (its scoped
    # Church Admin) instead of whoever is creating it - lets a Super Admin
    # register a church on a pastor/leader's behalf without the Super
    # Admin permanently sitting in that church's own membership list.
    admin_rooted_id: Optional[str] = Field(default=None, max_length=20)
    # Alternative to admin_rooted_id when that person hasn't signed up yet -
    # the moment someone signs up with this email, they're made this
    # church's owner automatically. Ignored if admin_rooted_id is also given.
    admin_email: Optional[str] = Field(default=None, max_length=255)


class ChurchOut(BaseModel):
    id: uuid.UUID
    name: str
    church_code: str
    description: Optional[str] = None
    address: Optional[str] = None
    privacy: str
    status: str
    member_count: int
    my_role: Optional[str] = None  # null if not a member (public discovery)
    # Only populated for this church's own owner/admin or a Super Admin -
    # null for anyone else, even other members.
    pending_admin_email: Optional[str] = None
    created_at: datetime


class ChurchUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    address: Optional[str] = Field(default=None, max_length=500)
    privacy: Optional[str] = Field(default=None, pattern="^(public|private|invite_only)$")
    status: Optional[str] = Field(default=None, pattern="^(active|suspended)$")
    # Corrects a mistyped pending admin invite (or sets a new one). If this
    # email already belongs to a Rooted account, that person becomes owner
    # immediately; otherwise it replaces the pending invite email.
    admin_email: Optional[str] = Field(default=None, max_length=255)


class ChurchMemberOut(BaseModel):
    user_id: str
    name: str
    photo_url: Optional[str] = None
    role: str
    joined_at: datetime


class ChurchDetailOut(ChurchOut):
    members: list[ChurchMemberOut] = []


# ---------------------------------------------------------------------
# Fellowship
# ---------------------------------------------------------------------
class FellowshipCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    church_id: Optional[uuid.UUID] = None
    privacy: str = Field(default="public", pattern="^(public|private|invite_only)$")
    # Same as Church.admin_rooted_id - assigns a specific person as this
    # fellowship's owner/admin instead of the creator.
    admin_rooted_id: Optional[str] = Field(default=None, max_length=20)
    # Same as Church.admin_email.
    admin_email: Optional[str] = Field(default=None, max_length=255)


class FellowshipOut(BaseModel):
    id: uuid.UUID
    name: str
    fellowship_code: str
    description: Optional[str] = None
    church_id: Optional[uuid.UUID] = None
    church_name: Optional[str] = None
    privacy: str
    status: str
    member_count: int
    my_role: Optional[str] = None
    pending_admin_email: Optional[str] = None
    created_at: datetime


class FellowshipUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    church_id: Optional[uuid.UUID] = None
    privacy: Optional[str] = Field(default=None, pattern="^(public|private|invite_only)$")
    status: Optional[str] = Field(default=None, pattern="^(active|suspended)$")
    # Same as ChurchUpdate.admin_email.
    admin_email: Optional[str] = Field(default=None, max_length=255)


class FellowshipDetailOut(FellowshipOut):
    members: list[ChurchMemberOut] = []


# ---------------------------------------------------------------------
# Rooted Group (Sunday / Blazer / Youth / Men / Women)
# ---------------------------------------------------------------------
class RootedGroupOut(BaseModel):
    id: uuid.UUID
    name: str
    sort_order: int


class MyGroupMembershipUpdate(BaseModel):
    group_ids: list[uuid.UUID] = Field(default_factory=list)


# ---------------------------------------------------------------------
# Active calendar - which org's own reading plan/quiz bank a member follows
# ---------------------------------------------------------------------
class CalendarOptionOut(BaseModel):
    kind: str  # "church" | "fellowship"
    org_id: uuid.UUID
    name: str


class ActiveCalendarUpdate(BaseModel):
    # null/null = the shared platform default
    kind: Optional[str] = Field(default=None, pattern="^(church|fellowship)$")
    org_id: Optional[uuid.UUID] = None


class InviteAdminByEmail(BaseModel):
    email: str = Field(min_length=3, max_length=255, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
