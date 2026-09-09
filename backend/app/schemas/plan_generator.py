from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field


class PlanGenerateRequest(BaseModel):
    section: Literal["new_testament", "full_bible", "gospels", "psalms", "custom"]
    custom_books: Optional[list[str]] = None  # only used when section == "custom"
    bible_version_code: str = "kjv1769"
    start_date: date
    duration_days: int = Field(gt=0, le=730)
    rest_day: Literal["none", "sunday", "one_per_week"] = "sunday"
    group_type: Literal["adult", "youth", "children", "family"] = "adult"


class PlanDayPreview(BaseModel):
    day_number: int
    reading_date: date
    old_testament: Optional[str] = None
    new_testament: Optional[str] = None
    is_rest_day: bool = False


class PlanPreviewResponse(BaseModel):
    total_days: int
    reading_days: int
    rest_days: int
    total_chapters: int
    approx_chapters_per_day: float
    days: list[PlanDayPreview]


class PlanCommitRequest(PlanGenerateRequest):
    """Same inputs as preview - regenerated server-side rather than trusting
    a client-submitted day list, so a tampered request can't inject arbitrary
    reading_plan rows."""
    pass
