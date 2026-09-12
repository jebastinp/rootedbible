from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_super_admin
from app.models.user import User
from app.schemas.plan_generator import PlanGenerateRequest, PlanCommitRequest, PlanPreviewResponse
from app.services.plan_generator_service import PlanGeneratorService

router = APIRouter(prefix="/admin/plan-generator", tags=["Admin - Plan Generator"])


@router.post("/preview", response_model=PlanPreviewResponse, summary="Preview a generated plan without saving it")
def preview_plan(
    payload: PlanGenerateRequest,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    return PlanGeneratorService(db).preview(payload)


@router.post("/commit", summary="Generate and save the plan - REPLACES the entire existing reading_plan table")
def commit_plan(
    payload: PlanCommitRequest,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    written = PlanGeneratorService(db).commit(payload, replace_existing=True)
    return {"success": True, "days_written": written}
