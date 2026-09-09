"""Synthetic fixtures only: no Bible text or licensing assertions."""
import copy
import hashlib
import json

import pytest

from app.content.validation import ContentValidationError, read_json, validate_dataset


def fixture():
    data = {
        "schema_version": 1, "translation_id": "synthetic", "dataset_version": "test-1",
        "books": [{"id": "test", "name": "Synthetic book", "testament": "OT", "chapters": [
            {"number": 1, "verses": [
                {"number": "1", "text": "தமிழ் சோதனை"},
                {"number": "2", "text": "മലയാളം പരിശോധന"},
                {"number": "3", "text": "हिन्दी परीक्षण"},
                {"number": "4", "text": "తెలుగు పరీక్ష"},
                {"number": "5", "text": "Synthetic English test."},
            ]},
        ]}],
    }
    manifest = {
        "schema_version": 1, "translation_id": "synthetic", "dataset_version": "test-1",
        "source_sha256": "0" * 64,
        "books": [{"id": "test", "name": "Synthetic book", "testament": "OT", "chapters": [
            {"number": 1, "verse_numbers": ["1", "2", "3", "4", "5"]},
        ]}],
    }
    return data, manifest


def test_valid_multilingual_structure_is_not_release_approval():
    data, manifest = fixture()
    result = validate_dataset(data, manifest, "0" * 64)
    assert result["verses"] == 5
    assert result["chapters"] == 1
    assert result["release_ready"] is False


@pytest.mark.parametrize("mutation", [
    lambda d: d["books"].append(copy.deepcopy(d["books"][0])),
    lambda d: d["books"][0]["chapters"].append(copy.deepcopy(d["books"][0]["chapters"][0])),
    lambda d: d["books"][0]["chapters"][0]["verses"].pop(),
    lambda d: d["books"][0]["chapters"][0]["verses"].reverse(),
    lambda d: d["books"][0]["chapters"][0]["verses"][0].update(number="2"),
    lambda d: d["books"][0]["chapters"][0].update(number=0),
    lambda d: d["books"][0].update(testament="NT"),
    lambda d: d.update(translation_id="different"),
    lambda d: d.update(dataset_version="different"),
])
def test_rejects_missing_duplicate_wrong_or_reordered_structure(mutation):
    data, manifest = fixture()
    mutation(data)
    with pytest.raises(ContentValidationError):
        validate_dataset(data, manifest, "0" * 64)


@pytest.mark.parametrize("text", ["", " ", " leading", "trailing ", "double  space", "bad\ufffd", "bad\ud800", "bad\x00", "bad\u202e"])
def test_rejects_empty_corrupt_or_unexpected_text_without_echoing_it(text):
    data, manifest = fixture()
    data["books"][0]["chapters"][0]["verses"][0]["text"] = text
    with pytest.raises(ContentValidationError) as exc:
        validate_dataset(data, manifest, "0" * 64)
    if text.strip():
        assert text not in str(exc.value)


def test_preserves_indic_joiners_and_reports_normalization_without_rewriting():
    data, manifest = fixture()
    text = "क्\u200dष e\u0301"
    data["books"][0]["chapters"][0]["verses"][0]["text"] = text
    result = validate_dataset(data, manifest, "0" * 64)
    assert result["warnings"]
    assert data["books"][0]["chapters"][0]["verses"][0]["text"] == text


def test_explicit_source_omissions_are_not_filled_with_invented_verses():
    data, manifest = fixture()
    data["books"][0]["chapters"][0]["verses"].pop(1)
    manifest["books"][0]["chapters"][0]["verse_numbers"].remove("2")
    assert validate_dataset(data, manifest, "0" * 64)["verses"] == 4


def test_wrong_checksum_is_rejected():
    data, manifest = fixture()
    with pytest.raises(ContentValidationError, match="checksum"):
        validate_dataset(data, manifest, "1" * 64)


@pytest.mark.parametrize("raw", [b'{"key":1,"key":2}', b'{"text":"\xff"}', b'not json'])
def test_strict_file_decode_and_duplicate_keys(tmp_path, raw):
    path = tmp_path / "input.json"
    path.write_bytes(raw)
    with pytest.raises(ContentValidationError):
        read_json(path)


def test_real_input_bytes_are_hashed(tmp_path):
    data, manifest = fixture()
    path = tmp_path / "synthetic.json"
    raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
    path.write_bytes(raw)
    parsed, checksum = read_json(path)
    manifest["source_sha256"] = hashlib.sha256(raw).hexdigest()
    assert validate_dataset(parsed, manifest, checksum)["structural_status"] == "passed"
