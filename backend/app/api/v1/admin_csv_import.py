from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_super_admin
from app.models.user import User
from app.schemas.misc import CsvPreviewResponse, CsvImportResult, ImportHistoryOut
from app.services.csv_import_service import CsvImportService

router = APIRouter(prefix="/admin/csv-import", tags=["Admin - CSV Import"])


@router.post("/preview", response_model=CsvPreviewResponse, summary="Upload + validate + preview a CSV before importing")
async def preview_csv(
    file_type: str = Form(..., description="users | reading_plan | progress | quiz"),
    file: UploadFile = File(...),
    version_code: str | None = Form(None, description="Required when file_type=quiz - Book/Chapter numbers are per Bible version"),
    db: Session = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    raw_bytes = await file.read()
    return CsvImportService(db).preview(file_type, file.filename, raw_bytes, version_code=version_code)


@router.post("/confirm", response_model=CsvImportResult, summary="Confirm and run the import for a previously previewed file")
def confirm_import(
    import_token: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    return CsvImportService(db).confirm(import_token, imported_by=current_user.id)


@router.get("/history", summary="Import history log")
def import_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_super_admin),
):
    items, total = CsvImportService(db).import_history(page, page_size)
    return {"items": [ImportHistoryOut.model_validate(i) for i in items], "total": total, "page": page, "page_size": page_size}
