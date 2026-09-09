import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd

from app.db.session import get_db
from app.api.deps import require_admin, require_leader_up
from app.models.user import User
from app.schemas.misc import AdminDashboardOut, MemberReportRow
from app.services.reports_service import ReportsService

router = APIRouter(prefix="/admin", tags=["Admin - Dashboard & Reports"])


@router.get("/dashboard", response_model=AdminDashboardOut, summary="Admin dashboard cards + charts data")
def dashboard(db: Session = Depends(get_db), _: User = Depends(require_leader_up)):
    return ReportsService(db).dashboard()


@router.get("/reports/members", response_model=list[MemberReportRow], summary="Full member report")
def member_report(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return ReportsService(db).member_report()


@router.get("/reports/inactive", response_model=list[MemberReportRow], summary="Members inactive for N+ days")
def inactive_report(days: int = 7, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return ReportsService(db).inactive_members(days)


@router.get("/reports/members/export", summary="Export the member report as an Excel file")
def export_member_report(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    rows = ReportsService(db).member_report()
    df = pd.DataFrame([r.model_dump() for r in rows])
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Member Report")
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=member_report.xlsx"},
    )
