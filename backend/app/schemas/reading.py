import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ReadingPlanBase(BaseModel):
    day_number: int = Field(gt=0)
    reading_date: date
    old_testament: Optional[str] = None
    new_testament: Optional[str] = None
    estimated_minutes: int = Field(default=15, ge=1, le=180)


class ReadingPlanCreate(ReadingPlanBase):
    pass


class ReadingPlanUpdate(BaseModel):
    reading_date: Optional[date] = None
    old_testament: Optional[str] = None
    new_testament: Optional[str] = None
    estimated_minutes: Optional[int] = Field(default=None, ge=1, le=180)


class PassageOut(BaseModel):
    """A validated, translation-independent Bible reference - e.g.
    {testament: "OT", book_name: "Genesis", chapter_start: 1, chapter_end: 3}.
    Used to deep-link straight into the Bible reader for a plan day."""
    model_config = ConfigDict(from_attributes=True)
    testament: str
    book_name: str
    chapter_start: int
    chapter_end: int


class ReadingPlanOut(ReadingPlanBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    passages: list[PassageOut] = []


class PlanDayOut(BaseModel):
    """One row in the member-facing 'View Full Plan' list."""
    id: uuid.UUID
    day_number: int
    reading_date: date
    old_testament: Optional[str]
    new_testament: Optional[str]
    estimated_minutes: int
    passages: list[PassageOut] = []
    completed: bool


class TodayReadingOut(BaseModel):
    """What a member sees on the Home screen."""
    id: uuid.UUID
    day_number: int
    reading_date: date
    old_testament: Optional[str]
    new_testament: Optional[str]
    estimated_minutes: int
    completed: bool
    completed_at: Optional[datetime] = None
    passages: list[PassageOut] = []


class MarkCompletedResponse(BaseModel):
    day_number: int
    completed: bool
    completed_at: datetime
    current_streak: int
    longest_streak: int
    overall_percentage: float
    days_completed: int


class ProgressStatsOut(BaseModel):
    overall_percentage: float
    current_streak: int
    longest_streak: int
    days_completed: int
    total_days: int
    ot_days_completed: int
    nt_days_completed: int
    ot_total: int
    nt_total: int
    books_completed: int
    books_total: int
    chapters_completed: int
    chapters_total: int
    last_completed_date: Optional[date] = None


class WeeklyProgressPoint(BaseModel):
    label: str  # e.g. "Mon" or week label
    date: date
    completed: bool


class MonthlyProgressPoint(BaseModel):
    month: str
    completion_percentage: float


class HeatmapEntry(BaseModel):
    date: date
    completed: bool


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    name: str
    photo_url: Optional[str] = None
    current_streak: int
    days_completed: int
    overall_percentage: float
