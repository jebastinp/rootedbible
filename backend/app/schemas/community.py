import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------
# Church
# ---------------------------------------------------------------------
class OrgAdminOut(BaseModel):
    """The one Rooted member currently assigned as this org's ADMIN - see
    AdminOrganizationAssignment. Null means no admin has been assigned yet."""
    user_id: str  # Rooted ID
    name: str
    email: Optional[str] = None


class ChurchCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    address: Optional[str] = Field(default=None, max_length=500)
    privacy: str = Field(default="public", pattern="^(public|private|invite_only)$")
    # Must belong to an EXISTING Rooted member - resolved immediately, or
    # this call fails with a clear error. There is no pending/placeholder
    # state; the member must register first, using this exact email.
    admin_rooted_id: Optional[str] = Field(default=None, max_length=20)
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
    # Only populated for this church's own admin or a Super Admin - null
    # for anyone else, even other members.
    admin: Optional[OrgAdminOut] = None
    created_at: datetime


class ChurchUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    address: Optional[str] = Field(default=None, max_length=500)
    privacy: Optional[str] = Field(default=None, pattern="^(public|private|invite_only)$")
    status: Optional[str] = Field(default=None, pattern="^(active|suspended)$")
    # Reassigns this church's admin. Must belong to an existing Rooted
    # member - resolved immediately or this call fails clearly. An empty
    # string removes the current admin (demoting them back to member).
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
    admin: Optional[OrgAdminOut] = None
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
