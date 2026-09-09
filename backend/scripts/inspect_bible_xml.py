"""Create a metadata-only inventory; never import or publish supplied text."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.content.xml_inventory import inspect_xml
from app.content.validation import ContentValidationError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    paths = sorted(args.folder.glob("*.xml"))
    if not paths:
        parser.error("No XML files found")
    reports = []
    for path in paths:
        try:
            report = inspect_xml(path)
            print(f"{path.name}: {report['books_observed']} books, {report['chapters_observed']} chapters, {report['verses_observed']} verses; {report['finding_count']} review findings")
        except (ContentValidationError, OSError) as exc:
            message = str(exc) if isinstance(exc, ContentValidationError) else "Unable to read input"
            report = {"file": path.name, "error": message, "release_ready": False}
            print(f"{path.name}: inspection failed")
        reports.append(report)
    args.report.write_text(json.dumps({"files": reports, "release_ready": False}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 1 if any("error" in report for report in reports) else 0


if __name__ == "__main__":
    raise SystemExit(main())
