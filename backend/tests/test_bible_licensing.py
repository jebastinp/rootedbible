import json
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.content.licensing import approved_web_codes, permits_stored_web_content
from app.core.exceptions import NotFoundError
from app.models.bible import BibleVersion
from app.repositories.bible_repository import BibleRepository
from app.services.bible_content_service import BibleContentService


def synthetic_grant():
    return {
        "translation_id": "synthetic", "translation_name": "Synthetic test only", "language": "en",
        "status": "approved", "qa_status": "approved", "copyright_owner": "Synthetic test",
        "provider": "Synthetic test", "license_type": "synthetic", "attribution_requirements": "Synthetic test",
        "copyright_notice": "Synthetic fixture, not a Bible license", "renewal_requirements": "Synthetic test",
        "evidence_location": "synthetic-only", "evidence_sha256": "0" * 64, "source_sha256": "1" * 64,
        "reviewer": "Synthetic reviewer", "dataset_version": "test-1", "source": "Synthetic test",
        "permissions": {scope: True for scope in ("display", "commercial", "caching", "storage", "distribution")},
        "territories": ["worldwide"], "user_limits": "unlimited", "api_rate_limits": "not_applicable",
        "valid_from": "2026-01-01", "reviewed_on": "2026-01-01", "expires_on": "2026-12-31",
    }


def test_scoped_synthetic_record_and_expiry():
    grant = synthetic_grant()
    assert permits_stored_web_content(grant, date(2026, 9, 8))
    assert not permits_stored_web_content(grant, date(2027, 1, 1))
    assert not permits_stored_web_content(grant, date(2025, 1, 1))


@pytest.mark.parametrize("field,value", [
    ("status", "pending"), ("qa_status", "pending"), ("evidence_location", None),
    ("evidence_sha256", "not-a-checksum"), ("source_sha256", None),
    ("reviewer", ""), ("copyright_notice", None), ("permissions", {}),
    ("territories", ["IN"]), ("user_limits", 100), ("api_rate_limits", 100),
    ("expires_on", None), ("valid_from", "invalid"), ("reviewed_on", "2030-01-01"),
])
def test_unknown_or_unsupported_scopes_fail_closed(field, value):
    grant = synthetic_grant()
    grant[field] = value
    assert not permits_stored_web_content(grant, date(2026, 9, 8))


def test_shipped_registry_grants_exactly_the_owner_attested_translations():
    """The registry originally shipped granting nothing (see git history) -
    the project owner explicitly reviewed and authorized flipping these 6
    translations open on 2026-09-09 via owner attestation (see
    licensing/evidence/2026-09-09-owner-attestation.md), after being told
    this bypasses the stricter third-party-evidence standard the gate was
    built for. This test pins the result to exactly that authorized set -
    if it fails, either a translation was authorized (update this test to
    match, deliberately) or the registry changed without authorization
    (investigate before touching this test)."""
    assert approved_web_codes() == frozenset({"nkjv", "kjv1769", "ta_bsi", "te_bsi", "kn_bsi", "hi_bsi"})


def test_missing_corrupt_or_duplicate_registry_fails_closed(tmp_path):
    path = tmp_path / "registry.json"
    assert approved_web_codes(path) == frozenset()
    path.write_text("invalid")
    assert approved_web_codes(path) == frozenset()
    path.write_text(json.dumps({"schema_version": 1, "translations": [synthetic_grant(), synthetic_grant()]}))
    assert approved_web_codes(path) == frozenset()


@pytest.fixture
def db():
    engine = create_engine("sqlite://")
    BibleVersion.__table__.create(engine)
    with Session(engine) as session:
        session.add_all([
            BibleVersion(code="pending", language="English", version_name="Synthetic pending", license_status="pending", is_active=True),
            BibleVersion(code="inactive", language="English", version_name="Synthetic inactive", license_status="licensed", is_active=False),
            BibleVersion(code="allowed", language="English", version_name="Synthetic allowed", license_status="licensed", is_active=True),
            BibleVersion(code="unreviewed", language="English", version_name="Synthetic unreviewed", license_status="public_domain", is_active=True),
        ])
        session.commit()
        yield session
    engine.dispose()


def test_catalog_and_direct_lookup_apply_identical_visibility_rules(db, monkeypatch):
    monkeypatch.setattr("app.repositories.bible_repository.approved_web_codes", lambda: frozenset({"pending", "inactive", "allowed"}))
    repo = BibleRepository(db)
    assert [v.code for v in repo.list_versions()] == ["allowed"]
    assert repo.get_version_by_code("allowed") is not None
    for code in ("pending", "inactive", "unreviewed", "unknown"):
        assert repo.get_version_by_code(code) is None


@pytest.mark.parametrize("method,args", [
    ("list_books", ("unreviewed",)),
    ("get_chapter", ("unreviewed", "Synthetic", 1)),
    ("get_navigation", ("unreviewed", "Synthetic", 1)),
])
def test_direct_service_endpoints_do_not_bypass_registry(db, method, args):
    with pytest.raises(NotFoundError):
        getattr(BibleContentService(db), method)(*args)
