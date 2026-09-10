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
    created_at: datetime


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


class FellowshipOut(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    church_id: Optional[uuid.UUID] = None
    church_name: Optional[str] = None
    privacy: str
    status: str
    member_count: int
    my_role: Optional[str] = None
    created_at: datetime


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
