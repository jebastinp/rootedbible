"""
Tests for CsvImportService's row-level validators. The DB session is
mocked (returning None for .first()) so these exercise the pure
validation rules without needing a real database.
"""
from unittest.mock import MagicMock

from app.services.csv_import_service import CsvImportService


def make_service_with_no_existing_records():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    return CsvImportService(db)


def test_valid_user_row_passes():
    service = make_service_with_no_existing_records()
    errors, action = service._validate_user_row({"user_id": "REH001", "name": "Rachel", "role": "member"})
    assert errors == []
    assert action == "insert"


def test_user_row_missing_user_id_fails():
    service = make_service_with_no_existing_records()
    errors, _ = service._validate_user_row({"user_id": "", "name": "Rachel", "role": "member"})
    assert "user_id is required" in errors


def test_user_row_missing_name_fails():
    service = make_service_with_no_existing_records()
    errors, _ = service._validate_user_row({"user_id": "REH001", "name": "", "role": "member"})
    assert "name is required" in errors


def test_user_row_invalid_role_fails():
    service = make_service_with_no_existing_records()
    errors, _ = service._validate_user_row({"user_id": "REH001", "name": "Rachel", "role": "pastor"})
    assert any("role" in e for e in errors)


def test_reading_plan_row_valid():
    service = make_service_with_no_existing_records()
    errors, action = service._validate_plan_row({"day": "1", "date": "2026-01-01"})
    assert errors == []
    assert action == "insert"


def test_reading_plan_row_invalid_day():
    service = make_service_with_no_existing_records()
    errors, _ = service._validate_plan_row({"day": "abc", "date": "2026-01-01"})
    assert any("day" in e for e in errors)


def test_reading_plan_row_invalid_date():
    service = make_service_with_no_existing_records()
    errors, _ = service._validate_plan_row({"day": "1", "date": "not-a-date"})
    assert any("date" in e for e in errors)


def test_progress_row_missing_user_fails():
    service = make_service_with_no_existing_records()
    errors, _ = service._validate_progress_row({"user_id": "", "day": "1"})
    assert any("user_id" in e for e in errors)
