from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.reading import ProgressStatsOut, HeatmapEntry, MonthlyProgressPoint
from app.services.progress_service import ProgressService

router = APIRouter(prefix="/progress", tags=["Progress (Member)"])


@router.get("/stats", response_model=ProgressStatsOut, summary="Overall %, streaks, OT/NT breakdown")
def stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ProgressService(db).get_progress_stats(current_user.id)


@router.get("/heatmap", response_model=list[HeatmapEntry], summary="Calendar heatmap data")
def heatmap(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ProgressService(db).get_heatmap(current_user.id)


@router.get("/monthly", response_model=list[MonthlyProgressPoint], summary="Monthly completion percentage series")
def monthly(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ProgressService(db).get_monthly_progress(current_user.id)
