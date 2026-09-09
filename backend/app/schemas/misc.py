import uuid
from datetime import date, datetime
from typing import Optional, List, Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.misc import AnnouncementVisibility, ImportStatus


class AnnouncementBase(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=2)
    publish_date: date = Field(default_factory=date.today)
    expiry_date: Optional[date] = None
    visibility: AnnouncementVisibility = AnnouncementVisibility.all
    is_active: bool = True


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    publish_date: Optional[date] = None
    expiry_date: Optional[date] = None
    visibility: Optional[AnnouncementVisibility] = None
    is_active: Optional[bool] = None


class AnnouncementOut(AnnouncementBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime


class ChurchSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    church_name: str
    church_logo_url: Optional[str] = None
    reading_year: int
    verse_of_the_day: Optional[str] = None


class ChurchSettingsUpdate(BaseModel):
    church_name: Optional[str] = None
    church_logo_url: Optional[str] = None
    reading_year: Optional[int] = None
    verse_of_the_day: Optional[str] = None


# ---------------------------------------------------------------------
# CSV Import
# ---------------------------------------------------------------------
class CsvPreviewRow(BaseModel):
    row_number: int
    data: dict[str, Any]
    valid: bool
    errors: List[str] = []
    action: str = "insert"  # insert | update | skip


class CsvPreviewResponse(BaseModel):
    file_type: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    rows: List[CsvPreviewRow]
    import_token: str  # opaque token referencing the parsed+validated dataset, used to confirm import


class CsvImportResult(BaseModel):
    file_type: str
    status: ImportStatus
    total_rows: int
    inserted_rows: int
    updated_rows: int
    skipped_rows: int
    failed_rows: int
    errors: List[str] = []


class ImportHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    file_type: str
    file_name: str
    status: ImportStatus
    total_rows: int
    inserted_rows: int
    updated_rows: int
    skipped_rows: int
    failed_rows: int
    created_at: datetime
    completed_at: Optional[datetime] = None


# ---------------------------------------------------------------------
# Reports / Dashboard
# ---------------------------------------------------------------------
class AdminDashboardOut(BaseModel):
    total_members: int
    todays_readers: int
    completion_percentage: float
    current_reading_day: Optional[int]
    average_streak: float
    recent_activities: List[dict]
    top_readers: List[dict]


class MemberReportRow(BaseModel):
    user_id: str
    name: str
    role: str
    status: str
    days_completed: int
    overall_percentage: float
    current_streak: int
    longest_streak: int
    last_completed_date: Optional[date] = None
