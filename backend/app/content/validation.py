"""Provider-independent structural QA. Does not fetch, publish, or rewrite text."""
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

MAX_SOURCE_BYTES = 100 * 1024 * 1024


class ContentValidationError(ValueError):
    pass


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Verse(StrictModel):
    number: str = Field(min_length=1)
    text: str = Field(min_length=1)


class Chapter(StrictModel):
    number: int = Field(gt=0)
    verses: list[Verse] = Field(min_length=1)


class Book(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9_-]+$")
    name: str = Field(min_length=1)
    testament: Literal["OT", "NT"]
    chapters: list[Chapter] = Field(min_length=1)


class Dataset(StrictModel):
    schema_version: Literal[1]
    translation_id: str = Field(pattern=r"^[a-z0-9_-]+$")
    dataset_version: str = Field(min_length=1)
    books: list[Book] = Field(min_length=1)


class ManifestChapter(StrictModel):
    number: int = Field(gt=0)
    # Labels are source-specific, including explicit omissions and bridges.
    verse_numbers: list[str] = Field(min_length=1)


class ManifestBook(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9_-]+$")
    name: str = Field(min_length=1)
    testament: Literal["OT", "NT"]
    chapters: list[ManifestChapter] = Field(min_length=1)


class Manifest(StrictModel):
    schema_version: Literal[1]
    translation_id: str = Field(pattern=r"^[a-z0-9_-]+$")
    dataset_version: str = Field(min_length=1)
    source_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    books: list[ManifestBook] = Field(min_length=1)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContentValidationError("Duplicate JSON object key")
        result[key] = value
    return result


def read_json(path: Path):
    if path.stat().st_size > MAX_SOURCE_BYTES:
        raise ContentValidationError("Input exceeds the 100 MiB validation limit")
    raw = path.read_bytes()
    if len(raw) > MAX_SOURCE_BYTES:
        raise ContentValidationError("Input exceeds the 100 MiB validation limit")
    try:
        data = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_unique_pairs)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ContentValidationError("Input must be valid UTF-8 JSON") from exc
    return data, hashlib.sha256(raw).hexdigest()


def _check_text(text: str, location: str, warnings: list[str]):
    # ZWJ/ZWNJ are intentionally permitted for Indic shaping. Never strip them.
    if not text.strip() or text != text.strip() or "  " in text:
        raise ContentValidationError(f"Empty or unexpected whitespace at {location}")
    if any(char == "\ufffd" or unicodedata.category(char) in ("Cc", "Cs", "Cn") for char in text):
        raise ContentValidationError(f"Invalid Unicode or control character at {location}")
    if any(unicodedata.category(char) == "Cf" and char not in "\u200c\u200d" for char in text):
        raise ContentValidationError(f"Unexpected formatting character at {location}")
    if not unicodedata.is_normalized("NFC", text):
        warnings.append(f"Source normalization requires human review at {location}; text was not modified")


def _same_unique(actual, expected, location):
    if len(set(actual)) != len(actual) or len(set(expected)) != len(expected):
        raise ContentValidationError(f"Duplicate identifier at {location}")
    if actual != expected:
        raise ContentValidationError(f"Missing, extra, or out-of-order content at {location}")


def validate_dataset(raw_dataset, raw_manifest, source_sha256: str) -> dict:
    try:
        dataset = Dataset.model_validate(raw_dataset)
        manifest = Manifest.model_validate(raw_manifest)
    except ValidationError as exc:
        # Validation payloads can contain complete verses. Never print them.
        raise ContentValidationError("Canonical dataset or manifest schema is invalid") from exc
    if (dataset.translation_id, dataset.dataset_version) != (manifest.translation_id, manifest.dataset_version):
        raise ContentValidationError("Dataset and manifest edition/version do not match")
    if source_sha256 != manifest.source_sha256:
        raise ContentValidationError("Source checksum does not match the approved manifest")

    warnings: list[str] = []
    chapters = verses = 0
    _same_unique([b.id for b in dataset.books], [b.id for b in manifest.books], "book list")
    for book, expected_book in zip(dataset.books, manifest.books):
        _check_text(book.name, f"{book.id} name", warnings)
        if (book.name, book.testament) != (expected_book.name, expected_book.testament):
            raise ContentValidationError(f"Book metadata mismatch at {book.id}")
        expected_chapters = [c.number for c in expected_book.chapters]
        if expected_chapters != list(range(1, len(expected_chapters) + 1)):
            raise ContentValidationError(f"Manifest chapter numbering is invalid at {book.id}")
        _same_unique([c.number for c in book.chapters], expected_chapters, book.id)
        for chapter, expected_chapter in zip(book.chapters, expected_book.chapters):
            location = f"{book.id}/{chapter.number}"
            # Allow source-declared 1a or 1-2 labels, never an empty/arbitrary label.
            if any(not re.fullmatch(r"[1-9][0-9]*(?:[a-z]|-[1-9][0-9]*)?", n) for n in expected_chapter.verse_numbers):
                raise ContentValidationError(f"Manifest verse labels are invalid at {location}")
            _same_unique([v.number for v in chapter.verses], expected_chapter.verse_numbers, location)
            for verse in chapter.verses:
                _check_text(verse.text, f"{location}/{verse.number}", warnings)
            chapters += 1
            verses += len(chapter.verses)
    return {
        "translation_id": dataset.translation_id,
        "dataset_version": dataset.dataset_version,
        "source_sha256": source_sha256,
        "books": len(dataset.books), "chapters": chapters, "verses": verses,
        "structural_status": "passed", "warnings": warnings,
        "release_ready": False,
        "remaining_review": "Written scoped rights, independent manifest provenance, source fidelity and human language QA are required.",
    }
