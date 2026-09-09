from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.reading import TodayReadingOut, MarkCompletedResponse, ProgressStatsOut, HeatmapEntry, MonthlyProgressPoint, PlanDayOut
from app.schemas.misc import AnnouncementOut
from app.services.progress_service import ProgressService
from app.services.announcement_service import AnnouncementService, SettingsService
from app.services.reading_plan_service import ReadingPlanService

router = APIRouter(prefix="/home", tags=["Home (Member)"])


@router.get("/today", response_model=TodayReadingOut, summary="Get today's reading + completion status")
def get_today_reading(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ProgressService(db).get_today_reading(current_user.id)


@router.post("/mark-completed", response_model=MarkCompletedResponse, summary="Mark today's reading as completed")
def mark_completed(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ProgressService(db).mark_today_completed(current_user.id)


@router.get("/plan", response_model=list[PlanDayOut], summary="Full reading plan with my completion status per day")
def get_full_plan(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ProgressService(db).get_full_plan(current_user.id)


@router.get("/summary", summary="Dashboard summary: streak, overall %, verse, announcements")
def home_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    progress_service = ProgressService(db)
    stats = progress_service.get_progress_stats(current_user.id)
    settings_row = SettingsService(db).get()
    announcements = AnnouncementService(db).list_active()

    return {
        "user_name": current_user.name,
        "stats": stats,
        "verse_of_the_day": settings_row.verse_of_the_day if settings_row else None,
        "church_name": settings_row.church_name if settings_row else "Rooted Church",
        "announcements": [AnnouncementOut.model_validate(a) for a in announcements[:3]],
    }
