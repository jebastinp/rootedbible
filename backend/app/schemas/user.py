import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import UserRole, UserStatus


class UserBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: UserRole = UserRole.member
    status: UserStatus = UserStatus.active
    date_of_birth: Optional[date] = None


class UserCreate(UserBase):
    user_id: str = Field(min_length=3, max_length=20, description="Login ID e.g. REH001")
    joined_date: Optional[date] = None


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    date_of_birth: Optional[date] = None
    photo_url: Optional[str] = None


class AdminAccountEmailUpdate(BaseModel):
    """Sets the Super Admin's own sign-in email from the dashboard. Kept
    separate from the general member self-service profile endpoint - this
    is the identity Supabase Auth links back to on next sign-in, not a
    display field members should be able to edit themselves."""
    email: str = Field(min_length=5, max_length=255)


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: str
    email: Optional[str] = None
    photo_url: Optional[str] = None
    joined_date: date
    created_at: datetime


class UserWithStats(UserOut):
    current_streak: int = 0
    longest_streak: int = 0
    days_completed: int = 0
    overall_percentage: float = 0


class LoginRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=20, description="Legacy member login ID, e.g. REH001 (staff/admin fallback only)")


class SupabaseLoginRequest(BaseModel):
    access_token: str = Field(min_length=10, description="Supabase Auth session access token (JWT), after signInWithOAuth")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut
    is_new_user: bool = False
    needs_onboarding: bool = False


class RefreshRequest(BaseModel):
    refresh_token: str
