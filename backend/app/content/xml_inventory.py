"""Inspect supplied XMLBIBLE files without importing or publishing Scripture.

Observed numbering is not an independently approved versification manifest.
The report deliberately contains no verse text.
"""
import hashlib
from collections import Counter
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

from app.content.validation import ContentValidationError, MAX_SOURCE_BYTES


def inspect_xml(path: Path) -> dict:
    if path.stat().st_size > MAX_SOURCE_BYTES:
        raise ContentValidationError("XML exceeds the validation size limit")
    raw = path.read_bytes()
    if len(raw) > MAX_SOURCE_BYTES:
        raise ContentValidationError("XML exceeds the validation size limit")
    try:
        decoded = raw.decode("utf-8-sig", errors="strict")
        if "<!DOCTYPE" in decoded.upper() or "<!ENTITY" in decoded.upper():
            raise ContentValidationError("XML document types and entity declarations are not supported")
        root = ET.fromstring(decoded)
    except (UnicodeError, ET.ParseError) as exc:
        raise ContentValidationError("File is not valid UTF-8 XML") from exc
    if root.tag != "XMLBIBLE":
        raise ContentValidationError("Expected XMLBIBLE source format")
    findings = []

    def sequence(elements, attr, location):
        numbers = []
        for element in elements:
            try:
                number = int(element.attrib[attr])
                if number < 1:
                    raise ValueError()
                numbers.append(number)
            except (KeyError, ValueError):
                findings.append({"location": location, "issue": f"Invalid or missing {attr}"})
        if len(numbers) != len(set(numbers)):
            findings.append({"location": location, "issue": f"Duplicate {attr}"})
        if numbers != sorted(numbers):
            findings.append({"location": location, "issue": f"Out-of-order {attr}"})
        if numbers and numbers != list(range(1, len(numbers) + 1)):
            findings.append({"location": location, "issue": f"Nonconsecutive {attr}; compare with approved source manifest"})
        return numbers

    books = root.findall("BIBLEBOOK")
    sequence(books, "bnumber", "books")
    if not books:
        findings.append({"location": "books", "issue": "No books found"})
    book_index = []
    chapter_total = verse_total = 0
    for book in books:
        book_number = book.get("bnumber", "unknown")
        chapters = book.findall("CHAPTER")
        sequence(chapters, "cnumber", f"book/{book_number}")
        if not chapters:
            findings.append({"location": f"book/{book_number}", "issue": "No chapters found"})
        chapter_index = []
        for chapter in chapters:
            chapter_number = chapter.get("cnumber", "unknown")
            location = f"book/{book_number}/chapter/{chapter_number}"
            verses = chapter.findall("VERS")
            sequence(verses, "vnumber", location)
            if not verses:
                findings.append({"location": location, "issue": "No verses found"})
            for verse in verses:
                text = "".join(verse.itertext())
                ref = f"{location}/verse/{verse.get('vnumber', 'unknown')}"
                if not text.strip():
                    findings.append({"location": ref, "issue": "Empty verse"})
                elif text != text.strip() or "  " in text or "\n" in text or "\t" in text:
                    findings.append({"location": ref, "issue": "Whitespace requires source review"})
                if any(char == "\ufffd" or unicodedata.category(char) in ("Cs", "Cn") for char in text):
                    findings.append({"location": ref, "issue": "Unicode requires source review"})
                if not unicodedata.is_normalized("NFC", text):
                    findings.append({"location": ref, "issue": "Non-NFC text; do not normalize without source review"})
            chapter_index.append({"number": chapter_number, "verses_observed": len(verses)})
            chapter_total += 1
            verse_total += len(verses)
        book_index.append({"number": book_number, "name": book.get("bname"), "chapters": chapter_index})
    return {
        "file": path.name, "source_sha256": hashlib.sha256(raw).hexdigest(),
        "format": "XMLBIBLE", "declared_name": root.get("biblename"),
        "books_observed": len(books), "chapters_observed": chapter_total, "verses_observed": verse_total,
        "metadata_elements": [child.tag for child in root if child.tag != "BIBLEBOOK"],
        "finding_count": len(findings),
        "finding_counts": dict(Counter(finding["issue"] for finding in findings)),
        "findings": findings[:50], "findings_sample_limit": 50, "observed_index": book_index,
        "license_status": "unverified", "source_fidelity": "unverified", "release_ready": False,
    }
