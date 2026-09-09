"""
CSV Import Wizard backend logic.

Flow:
  1. POST /csv/preview  -> parses + validates the file, stores the parsed
     rows in a short-lived in-memory cache keyed by an import_token, and
     returns a preview (first N rows + full validation summary) to the UI.
  2. POST /csv/confirm  -> takes the import_token, re-validates, and runs
     the actual insert/update inside a single DB transaction. On any
     unexpected error the whole transaction is rolled back and the
     import_history row is marked 'failed'.

NOTE: the in-memory cache (_IMPORT_CACHE) is fine for a single-process
deployment. For multi-worker / multi-instance production deployments,
swap this for Redis (the interface is intentionally tiny - get/set/pop).
"""
import io
import time
import uuid
from datetime import datetime, date
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationError, NotFoundError
from app.models.misc import ImportHistory, ImportStatus
from app.models.user import User, UserRole, UserStatus
from app.models.reading_plan import ReadingPlan
from app.models.progress import ReadingProgress
from app.schemas.misc import CsvPreviewResponse, CsvPreviewRow, CsvImportResult
from app.services.progress_service import ProgressService

_IMPORT_CACHE: dict[str, dict[str, Any]] = {}
_CACHE_TTL_SECONDS = 60 * 30  # 30 minutes


def _cache_set(token: str, payload: dict) -> None:
    _IMPORT_CACHE[token] = {"payload": payload, "ts": time.time()}


def _cache_get(token: str) -> dict | None:
    entry = _IMPORT_CACHE.get(token)
    if not entry:
        return None
    if time.time() - entry["ts"] > _CACHE_TTL_SECONDS:
        _IMPORT_CACHE.pop(token, None)
        return None
    return entry["payload"]


REQUIRED_COLUMNS = {
    "users": {"user_id", "name"},
    "reading_plan": {"day", "date"},
    "progress": {"user_id", "day"},
}


class CsvImportService:
    def __init__(self, db: Session):
        self.db = db

    # -----------------------------------------------------------------
    def preview(self, file_type: str, filename: str, raw_bytes: bytes) -> CsvPreviewResponse:
        if file_type not in REQUIRED_COLUMNS:
            raise ValidationError(f"Unsupported file_type '{file_type}'. Must be one of: users, reading_plan, progress")

        try:
            df = pd.read_csv(io.BytesIO(raw_bytes), dtype=str, keep_default_na=False)
        except Exception as exc:
            raise ValidationError(f"Could not parse CSV file: {exc}")

        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        missing = REQUIRED_COLUMNS[file_type] - set(df.columns)
        if missing:
            raise ValidationError(f"Missing required column(s): {', '.join(sorted(missing))}")

        rows: list[CsvPreviewRow] = []
        valid_records: list[dict] = []

        validator = {
            "users": self._validate_user_row,
            "reading_plan": self._validate_plan_row,
            "progress": self._validate_progress_row,
        }[file_type]

        for idx, row in df.iterrows():
            record = row.to_dict()
            errors, action = validator(record)
            is_valid = len(errors) == 0
            if is_valid:
                valid_records.append(record)
            rows.append(
                CsvPreviewRow(row_number=idx + 1, data=record, valid=is_valid, errors=errors, action=action)
            )

        import_token = str(uuid.uuid4())
        _cache_set(
            import_token,
            {
                "file_type": file_type,
                "filename": filename,
                "valid_records": valid_records,
                "total_rows": len(rows),
                "invalid_rows": sum(1 for r in rows if not r.valid),
            },
        )

        return CsvPreviewResponse(
            file_type=file_type,
            total_rows=len(rows),
            valid_rows=len(valid_records),
            invalid_rows=sum(1 for r in rows if not r.valid),
            rows=rows[:200],  # cap preview payload size
            import_token=import_token,
        )

    # -----------------------------------------------------------------
    def confirm(self, import_token: str, imported_by: uuid.UUID | None = None) -> CsvImportResult:
        cached = _cache_get(import_token)
        if not cached:
            raise NotFoundError("Import session expired or not found. Please re-upload the file.")

        file_type = cached["file_type"]
        history = ImportHistory(
            file_type=file_type,
            file_name=cached["filename"],
            status=ImportStatus.processing,
            total_rows=cached["total_rows"],
            failed_rows=cached["invalid_rows"],
            imported_by=imported_by,
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)

        inserted = updated = skipped = 0
        errors: list[str] = []

        try:
            if file_type == "users":
                inserted, updated, skipped, errors = self._import_users(cached["valid_records"])
            elif file_type == "reading_plan":
                inserted, updated, skipped, errors = self._import_reading_plan(cached["valid_records"])
            elif file_type == "progress":
                inserted, updated, skipped, errors = self._import_progress(cached["valid_records"])

            history.status = ImportStatus.success if not errors else ImportStatus.success
            history.inserted_rows = inserted
            history.updated_rows = updated
            history.skipped_rows = skipped
            history.error_log = {"errors": errors} if errors else None
            history.completed_at = datetime.utcnow()
            self.db.commit()

        except Exception as exc:
            self.db.rollback()
            history.status = ImportStatus.rolled_back
            history.error_log = {"errors": [str(exc)]}
            history.completed_at = datetime.utcnow()
            self.db.commit()
            raise

        _IMPORT_CACHE.pop(import_token, None)

        return CsvImportResult(
            file_type=file_type,
            status=history.status,
            total_rows=history.total_rows,
            inserted_rows=inserted,
            updated_rows=updated,
            skipped_rows=skipped,
            failed_rows=history.failed_rows,
            errors=errors,
        )

    def import_history(self, page: int = 1, page_size: int = 20):
        query = self.db.query(ImportHistory).order_by(ImportHistory.created_at.desc())
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    # -----------------------------------------------------------------
    # VALIDATORS
    # -----------------------------------------------------------------
    def _validate_user_row(self, record: dict) -> tuple[list[str], str]:
        errors = []
        if not record.get("user_id", "").strip():
            errors.append("user_id is required")
        if not record.get("name", "").strip():
            errors.append("name is required")
        role = record.get("role", "member").strip().lower() or "member"
        if role not in UserRole.__members__:
            errors.append(f"role '{role}' is invalid (must be member/leader/admin/super_admin)")
        existing = self.db.query(User).filter(User.user_id == record.get("user_id", "").strip().upper()).first()
        action = "update" if existing else "insert"
        return errors, action

    def _validate_plan_row(self, record: dict) -> tuple[list[str], str]:
        errors = []
        try:
            day = int(record.get("day", "").strip())
            if day <= 0:
                errors.append("day must be a positive integer")
        except (ValueError, AttributeError):
            errors.append("day must be a valid integer")
            day = None
        try:
            pd.to_datetime(record.get("date", ""))
        except Exception:
            errors.append("date is not a valid date")
        existing = None
        if day is not None:
            existing = self.db.query(ReadingPlan).filter(ReadingPlan.day_number == day).first()
        action = "update" if existing else "insert"
        return errors, action

    def _validate_progress_row(self, record: dict) -> tuple[list[str], str]:
        errors = []
        user_code = record.get("user_id", "").strip().upper()
        if not user_code:
            errors.append("user_id is required")
        else:
            user = self.db.query(User).filter(User.user_id == user_code).first()
            if not user:
                errors.append(f"user_id '{user_code}' does not exist - import users.csv first")
        try:
            day = int(record.get("day", "").strip())
        except (ValueError, AttributeError):
            errors.append("day must be a valid integer")
            day = None
        if day is not None:
            plan = self.db.query(ReadingPlan).filter(ReadingPlan.day_number == day).first()
            if not plan:
                errors.append(f"day {day} does not exist in reading_plan - import reading_plan.csv first")
        return errors, "upsert"

    # -----------------------------------------------------------------
    # IMPORTERS (upsert semantics)
    # -----------------------------------------------------------------
    def _import_users(self, records: list[dict]):
        inserted = updated = skipped = 0
        errors: list[str] = []
        for r in records:
            try:
                user_code = r["user_id"].strip().upper()
                existing = self.db.query(User).filter(User.user_id == user_code).first()
                role = (r.get("role") or "member").strip().lower()
                joined = r.get("joined_date", "").strip()
                joined_date = pd.to_datetime(joined).date() if joined else date.today()

                if existing:
                    existing.name = r.get("name", existing.name).strip() or existing.name
                    existing.phone = r.get("phone", existing.phone) or existing.phone
                    existing.role = UserRole(role)
                    updated += 1
                else:
                    user = User(
                        user_id=user_code,
                        name=r["name"].strip(),
                        phone=r.get("phone") or None,
                        role=UserRole(role),
                        status=UserStatus.active,
                        joined_date=joined_date,
                    )
                    self.db.add(user)
                    self.db.flush()
                    from app.models.progress import UserStats
                    self.db.add(UserStats(user_id=user.id))
                    inserted += 1
            except Exception as exc:
                skipped += 1
                errors.append(f"user_id={r.get('user_id')}: {exc}")
        self.db.commit()
        return inserted, updated, skipped, errors

    def _import_reading_plan(self, records: list[dict]):
        inserted = updated = skipped = 0
        errors: list[str] = []
        for r in records:
            try:
                day = int(r["day"])
                reading_date = pd.to_datetime(r["date"]).date()
                existing = self.db.query(ReadingPlan).filter(ReadingPlan.day_number == day).first()
                est_minutes = int(r.get("estimated_minutes") or 15)
                if existing:
                    existing.reading_date = reading_date
                    existing.old_testament = r.get("old_testament") or existing.old_testament
                    existing.new_testament = r.get("new_testament") or existing.new_testament
                    existing.estimated_minutes = est_minutes
                    updated += 1
                else:
                    plan = ReadingPlan(
                        day_number=day,
                        reading_date=reading_date,
                        old_testament=r.get("old_testament") or None,
                        new_testament=r.get("new_testament") or None,
                        estimated_minutes=est_minutes,
                    )
                    self.db.add(plan)
                    inserted += 1
            except Exception as exc:
                skipped += 1
                errors.append(f"day={r.get('day')}: {exc}")
        self.db.commit()
        return inserted, updated, skipped, errors

    def _import_progress(self, records: list[dict]):
        inserted = updated = skipped = 0
        errors: list[str] = []
        affected_users: set[uuid.UUID] = set()

        for r in records:
            try:
                user_code = r["user_id"].strip().upper()
                day = int(r["day"])
                user = self.db.query(User).filter(User.user_id == user_code).first()
                plan = self.db.query(ReadingPlan).filter(ReadingPlan.day_number == day).first()
                if not user or not plan:
                    skipped += 1
                    continue

                completed_flag = str(r.get("completed", "true")).strip().lower() in ("true", "1", "yes", "y")
                completed_date_raw = r.get("completed_date", "").strip()
                completed_at = pd.to_datetime(completed_date_raw) if completed_date_raw else datetime.utcnow()

                existing = (
                    self.db.query(ReadingProgress)
                    .filter(ReadingProgress.user_id == user.id, ReadingProgress.reading_plan_id == plan.id)
                    .first()
                )
                if existing:
                    existing.completed = completed_flag
                    existing.completed_at = completed_at if completed_flag else None
                    updated += 1
                else:
                    entry = ReadingProgress(
                        user_id=user.id,
                        reading_plan_id=plan.id,
                        day_number=day,
                        completed=completed_flag,
                        completed_at=completed_at if completed_flag else None,
                    )
                    self.db.add(entry)
                    inserted += 1
                affected_users.add(user.id)
            except Exception as exc:
                skipped += 1
                errors.append(f"user_id={r.get('user_id')}, day={r.get('day')}: {exc}")

        self.db.commit()

        # Recalculate streaks/percentages for every affected user
        progress_service = ProgressService(self.db)
        for user_id in affected_users:
            progress_service.recalculate_stats(user_id)

        return inserted, updated, skipped, errors
