"""
Imports the local Zefania-XMLBIBLE-format Bible files in bible/ into the
normalized bible_version -> bible_book -> bible_chapter -> bible_verse schema.

The XML is treated as read-only source data and is never modified. Whatever
is actually present in a file is what gets imported - missing verses,
missing chapters, and encoding defects are reported, never fabricated or
silently patched over.

Usage:
    python scripts/import_bible_xml.py --all
    python scripts/import_bible_xml.py --code nkjv
"""
import argparse
import hashlib
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.models.bible import BibleVersion, BibleBook, BibleChapter, BibleVerse

BIBLE_DIR = Path(__file__).resolve().parents[2] / "bible"

# Maps each known local source file to the bible_version.code it populates.
# This is the one place we assert "this file IS this catalog entry" - book
# names, chapter counts, and verse text all come from the file itself, not
# from this mapping.
SOURCE_MAP = {
    "kjv1769": BIBLE_DIR / "21st Century KJV.xml",  # actually KJ21 (1994), not the public-domain 1769 KJV - see version_name
    "nkjv": BIBLE_DIR / "New King James Version (1982).xml",
    "ta_bsi": BIBLE_DIR / "Tamil Bible.xml",
    "te_bsi": BIBLE_DIR / "Telugu Bible (BSI).xml",
    "kn_bsi": BIBLE_DIR / "Kannada Bible.xml",
    "hi_bsi": BIBLE_DIR / "Hindi Bible.xml",
}

# Verified against every source file: book numbering is sequential 1-66,
# and book 40 (Matthew) is always the first New Testament book.
NT_START_BOOK_NUMBER = 40


@dataclass
class ImportReport:
    code: str
    file: str
    source_sha256: str = ""
    books: int = 0
    chapters: int = 0
    verses: int = 0
    empty_verses_skipped: int = 0
    missing_verse_numbers: list = field(default_factory=list)
    encoding_warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)


def parse_source(path: Path) -> ET.Element:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    return ET.fromstring(text)


def import_version(db, code: str, path: Path) -> ImportReport:
    raw = path.read_bytes()
    report = ImportReport(code=code, file=path.name, source_sha256=hashlib.sha256(raw).hexdigest())

    version = db.query(BibleVersion).filter(BibleVersion.code == code).first()
    if not version:
        report.errors.append(f"No bible_version row for code={code!r} - seed it first")
        return report

    try:
        root = ET.fromstring(raw.decode("utf-8-sig"))
    except (UnicodeError, ET.ParseError) as exc:
        report.errors.append(f"Could not parse XML: {exc}")
        return report
    if root.tag != "XMLBIBLE":
        report.errors.append(f"Unexpected root tag {root.tag!r}, expected XMLBIBLE")
        return report

    # Re-importing replaces this version's content, so the command is safe to re-run.
    db.query(BibleBook).filter(BibleBook.bible_version_id == version.id).delete()
    db.flush()

    for xml_book in root.findall("BIBLEBOOK"):
        try:
            bnumber = int(xml_book.get("bnumber"))
        except (TypeError, ValueError):
            report.errors.append(f"Book missing/invalid bnumber (bname={xml_book.get('bname')!r})")
            continue
        bname = (xml_book.get("bname") or "").strip()
        if not bname:
            report.errors.append(f"Book {bnumber} has no bname")
            continue

        xml_chapters = xml_book.findall("CHAPTER")
        book = BibleBook(
            bible_version_id=version.id,
            name=bname,
            testament="OT" if bnumber < NT_START_BOOK_NUMBER else "NT",
            sort_order=bnumber,
            chapter_count=len(xml_chapters),
        )
        db.add(book)
        db.flush()
        report.books += 1

        for xml_chapter in xml_chapters:
            try:
                cnumber = int(xml_chapter.get("cnumber"))
            except (TypeError, ValueError):
                report.errors.append(f"{bname}: chapter missing/invalid cnumber")
                continue

            chapter = BibleChapter(book_id=book.id, chapter_number=cnumber)
            db.add(chapter)
            db.flush()
            report.chapters += 1

            seen_numbers = []
            for xml_verse in xml_chapter.findall("VERS"):
                try:
                    vnumber = int(xml_verse.get("vnumber"))
                except (TypeError, ValueError):
                    report.errors.append(f"{bname} {cnumber}: verse missing/invalid vnumber")
                    continue
                text = "".join(xml_verse.itertext()).strip()
                if not text:
                    report.empty_verses_skipped += 1
                    continue
                if "�" in text:
                    report.encoding_warnings.append(f"{bname} {cnumber}:{vnumber}")
                db.add(BibleVerse(chapter_id=chapter.id, verse_number=vnumber, text=text))
                report.verses += 1
                seen_numbers.append(vnumber)

            if seen_numbers:
                expected = set(range(min(seen_numbers), max(seen_numbers) + 1))
                for missing in sorted(expected - set(seen_numbers)):
                    report.missing_verse_numbers.append(f"{bname} {cnumber}:{missing}")

    db.commit()
    return report


def print_report(report: ImportReport) -> None:
    print(f"{report.code} ({report.file}): {report.books} books, {report.chapters} chapters, {report.verses} verses")
    if report.empty_verses_skipped:
        print(f"  empty verses in source (skipped, not fabricated): {report.empty_verses_skipped}")
    if report.missing_verse_numbers:
        sample = report.missing_verse_numbers[:10]
        more = f" (+{len(report.missing_verse_numbers) - 10} more)" if len(report.missing_verse_numbers) > 10 else ""
        print(f"  verse numbers absent from source entirely: {sample}{more}")
    if report.encoding_warnings:
        print(f"  possible encoding corruption (U+FFFD found): {report.encoding_warnings}")
    if report.errors:
        print(f"  ERRORS: {report.errors}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--code", help="Import only this bible_version code")
    parser.add_argument("--all", action="store_true", help="Import every known source file")
    args = parser.parse_args()

    if not args.all and not args.code:
        parser.error("Pass --all or --code <version_code>")

    codes = list(SOURCE_MAP.keys()) if args.all else [args.code]
    db = SessionLocal()
    reports = []
    try:
        for code in codes:
            path = SOURCE_MAP.get(code)
            if not path:
                print(f"{code}: no known source file mapped")
                continue
            if not path.exists():
                print(f"{code}: source file not found at {path}")
                continue
            report = import_version(db, code, path)
            reports.append(report)
            print_report(report)
    finally:
        db.close()

    return 1 if any(r.errors for r in reports) else 0


if __name__ == "__main__":
    raise SystemExit(main())
