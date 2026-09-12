"""Per-organization admin management: each Church/Fellowship's own owner/
admin can run their OWN reading-plan calendar and quiz question bank,
completely separate from the shared platform ones and from every other
org's - gated by CommunityService._require_admin, the same per-org
ownership check every other Church/Fellowship admin action uses (never the
platform-wide require_admin dependency)."""
import uuid

from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.reading import ReadingPlanOut, ReadingPlanCreate, ReadingPlanUpdate
from app.schemas.quiz import QuizQuestionAdminOut, QuizQuestionCreate, QuizQuestionUpdate
from app.schemas.community import InviteAdminByEmail
from app.schemas.misc import CsvPreviewResponse, CsvImportResult
from app.services.community_service import CommunityService
from app.services.reading_plan_service import ReadingPlanService
from app.services.quiz_service import QuizService
from app.services.csv_import_service import CsvImportService

router = APIRouter(prefix="/community", tags=["Org Admin - Reading Plan & Quiz"])


def _require_org_admin(kind: str, org_id: uuid.UUID, current_user: User, db: Session) -> None:
    CommunityService(db)._require_admin(kind, org_id, current_user.id)


def _plan_service(kind: str, org_id: uuid.UUID, db: Session) -> ReadingPlanService:
    return ReadingPlanService(db, church_id=org_id if kind == "church" else None, fellowship_id=org_id if kind == "fellowship" else None)


def _quiz_service(kind: str, org_id: uuid.UUID, db: Session) -> QuizService:
    return QuizService(db, church_id=org_id if kind == "church" else None, fellowship_id=org_id if kind == "fellowship" else None)


# -----------------------------------------------------------------------
# Reading Plan - one org's own calendar
# -----------------------------------------------------------------------
def _register_reading_plan_routes(kind: str) -> None:
    prefix = f"/{kind}/{{org_id}}/reading-plan"

    @router.get(prefix, response_model=dict, summary=f"List this {kind}'s own reading plan days")
    def list_plan(org_id: uuid.UUID, search: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(30, ge=1, le=200), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        _require_org_admin(kind, org_id, current_user, db)
        items, total = _plan_service(kind, org_id, db).list(search, page, page_size)
        return {"items": [ReadingPlanOut.model_validate(p) for p in items], "total": total, "page": page, "page_size": page_size}

    @router.post(prefix, response_model=ReadingPlanOut, summary=f"Add a day to this {kind}'s reading plan")
    def create_plan_day(org_id: uuid.UUID, payload: ReadingPlanCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        _require_org_admin(kind, org_id, current_user, db)
        return _plan_service(kind, org_id, db).create(payload)

    @router.patch(prefix + "/{plan_id}", response_model=ReadingPlanOut, summary=f"Edit a day in this {kind}'s reading plan")
    def update_plan_day(org_id: uuid.UUID, plan_id: uuid.UUID, payload: ReadingPlanUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        _require_org_admin(kind, org_id, current_user, db)
        return _plan_service(kind, org_id, db).update(plan_id, payload)

    @router.delete(prefix + "/{plan_id}", summary=f"Delete a day from this {kind}'s reading plan")
    def delete_plan_day(org_id: uuid.UUID, plan_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        _require_org_admin(kind, org_id, current_user, db)
        _plan_service(kind, org_id, db).delete(plan_id)
        return {"message": "Reading day deleted successfully"}


# -----------------------------------------------------------------------
# Quiz - one org's own question bank
# -----------------------------------------------------------------------
def _register_quiz_routes(kind: str) -> None:
    prefix = f"/{kind}/{{org_id}}/quiz"

    @router.get(prefix + "/chapter", response_model=list[QuizQuestionAdminOut], summary=f"List this {kind}'s own quiz questions for a chapter")
    def list_questions(org_id: uuid.UUID, version_code: str = Query(...), book_name: str = Query(...), chapter_number: int = Query(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        _require_org_admin(kind, org_id, current_user, db)
        service = _quiz_service(kind, org_id, db)
        chapter_id = service.resolve_chapter_id(version_code, book_name, chapter_number)
        return service.admin_list_questions_for_chapter(chapter_id)

    @router.post(prefix + "/chapter", response_model=QuizQuestionAdminOut, summary=f"Add a quiz question to this {kind}'s own bank")
    def create_question(org_id: uuid.UUID, payload: QuizQuestionCreate, version_code: str = Query(...), book_name: str = Query(...), chapter_number: int = Query(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        _require_org_admin(kind, org_id, current_user, db)
        service = _quiz_service(kind, org_id, db)
        chapter_id = service.resolve_chapter_id(version_code, book_name, chapter_number)
        return service.admin_create_question(current_user.id, chapter_id, payload)

    @router.patch(prefix + "/{question_id}", response_model=QuizQuestionAdminOut, summary=f"Update a question in this {kind}'s own bank")
    def update_question(org_id: uuid.UUID, question_id: uuid.UUID, payload: QuizQuestionUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        _require_org_admin(kind, org_id, current_user, db)
        return _quiz_service(kind, org_id, db).admin_update_question(current_user.id, question_id, payload)

    @router.delete(prefix + "/{question_id}", summary=f"Delete a question from this {kind}'s own bank")
    def delete_question(org_id: uuid.UUID, question_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        _require_org_admin(kind, org_id, current_user, db)
        _quiz_service(kind, org_id, db).admin_delete_question(current_user.id, question_id)
        return {"success": True}


def _register_quiz_csv_routes(kind: str) -> None:
    prefix = f"/{kind}/{{org_id}}/quiz/csv-import"

    @router.post(prefix + "/preview", response_model=CsvPreviewResponse, summary=f"Upload + validate + preview a bulk quiz CSV for this {kind}'s own bank")
    async def preview_quiz_csv(org_id: uuid.UUID, file: UploadFile = File(...), version_code: str = Form(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        _require_org_admin(kind, org_id, current_user, db)
        raw_bytes = await file.read()
        return CsvImportService(db).preview(
            "quiz", file.filename, raw_bytes, version_code=version_code,
            church_id=org_id if kind == "church" else None, fellowship_id=org_id if kind == "fellowship" else None,
        )

    @router.post(prefix + "/confirm", response_model=CsvImportResult, summary=f"Confirm a previously previewed bulk quiz CSV for this {kind}'s own bank")
    def confirm_quiz_csv(org_id: uuid.UUID, import_token: str = Form(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        _require_org_admin(kind, org_id, current_user, db)
        return CsvImportService(db).confirm(import_token, imported_by=current_user.id)


def _register_admin_invite_route(kind: str) -> None:
    @router.post(f"/{kind}/{{org_id}}/invite-admin-by-email", summary=f"Add another admin to this {kind} by email (they must already have a Rooted account)")
    def invite_admin(org_id: uuid.UUID, payload: InviteAdminByEmail, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        CommunityService(db).invite_admin_by_email(current_user.id, kind, org_id, payload.email)
        return {"success": True}


for _kind in ("church", "fellowship"):
    _register_reading_plan_routes(_kind)
    _register_quiz_routes(_kind)
    _register_quiz_csv_routes(_kind)
    _register_admin_invite_route(_kind)
