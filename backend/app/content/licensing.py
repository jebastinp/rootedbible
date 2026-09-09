"""Fail closed until a reviewed edition is approved for this deployment.

This gate supports unrestricted-user, worldwide, stored-text deployments only.
Restricted territories/usage limits require an enforcement adapter before release.
A database label is never evidence of permission.
"""
import json
import os
import re
from datetime import date
from pathlib import Path

REGISTRY_PATH = Path(os.environ.get(
    "ROOTED_LICENSE_REGISTRY",
    str(Path(__file__).resolve().parents[3] / "licensing" / "translations.json"),
))


def permits_stored_web_content(record: dict, today: date | None = None) -> bool:
    today = today or date.today()
    if record.get("status") != "approved" or record.get("qa_status") != "approved":
        return False
    required = (
        "translation_id", "translation_name", "language", "copyright_owner",
        "provider", "license_type", "attribution_requirements", "copyright_notice",
        "renewal_requirements", "evidence_location", "reviewer", "dataset_version", "source",
    )
    if any(not isinstance(record.get(key), str) or not record[key].strip() for key in required):
        return False
    for key in ("evidence_sha256", "source_sha256"):
        if not re.fullmatch(r"[a-f0-9]{64}", str(record.get(key, ""))):
            return False
    # Current reader keeps queries in memory and backend stores chapter text.
    # Native/offline/limited-use deployments are deliberately not cleared here.
    permissions = record.get("permissions")
    if not isinstance(permissions, dict) or any(
        permissions.get(scope) is not True
        for scope in ("display", "commercial", "caching", "storage", "distribution")
    ):
        return False
    if record.get("territories") != ["worldwide"] or record.get("user_limits") != "unlimited":
        return False
    if record.get("api_rate_limits") != "not_applicable":
        return False
    try:
        valid_from = date.fromisoformat(record["valid_from"])
        reviewed = date.fromisoformat(record["reviewed_on"])
        if valid_from > today or reviewed > today:
            return False
        expiry = record.get("expires_on")
        if expiry is None:
            return record.get("perpetual") is True
        expires_on = date.fromisoformat(expiry)
        return valid_from <= expires_on and today <= expires_on
    except (ValueError, TypeError, KeyError):
        return False


def approved_web_codes(path: Path = REGISTRY_PATH) -> frozenset[str]:
    # Re-read to honor withdrawal without retaining an authorization cache.
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(registry, dict) or registry.get("schema_version") != 1:
            return frozenset()
        records = registry["translations"]
        if not isinstance(records, list):
            return frozenset()
        codes = [record.get("translation_id") for record in records if isinstance(record, dict)]
        if len(codes) != len(records) or any(not isinstance(code, str) for code in codes):
            return frozenset()
        if len(set(codes)) != len(codes):
            return frozenset()
        return frozenset(record["translation_id"] for record in records if permits_stored_web_content(record))
    except (OSError, ValueError, KeyError, TypeError):
        return frozenset()
