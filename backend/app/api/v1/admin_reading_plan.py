import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_super_admin
from app.models.user import User
from app.schemas.reading import ReadingPlanOut, ReadingPlanCreate, ReadingPlanUpdate
from app.services.reading_plan_service import ReadingPlanService

router = APIRouter(prefix="/admin/reading-plan", tags=["Admin - Reading Plan"])


@router.get("", summary="List reading plan days (search, paginated)")
def list_plan(
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    items, total = ReadingPlanService(db).list(search, page, page_size)
    return {
        "items": [ReadingPlanOut.model_validate(p) for p in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("", response_model=ReadingPlanOut, summary="Add a reading day")
def create_plan_day(payload: ReadingPlanCreate, db: Session = Depends(get_db), _: User = Depends(require_super_admin)):
    return ReadingPlanService(db).create(payload)


@router.patch("/{plan_id}", response_model=ReadingPlanOut, summary="Edit a reading day")
def update_plan_day(plan_id: uuid.UUID, payload: ReadingPlanUpdate, db: Session = Depends(get_db), _: User = Depends(require_super_admin)):
    return ReadingPlanService(db).update(plan_id, payload)


@router.delete("/{plan_id}", summary="Delete a reading day")
def delete_plan_day(plan_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_super_admin)):
    ReadingPlanService(db).delete(plan_id)
    return {"message": "Reading day deleted successfully"}
