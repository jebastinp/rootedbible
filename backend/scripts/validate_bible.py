"""Validate local canonical content; no downloads or database mutations."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.content.validation import ContentValidationError, read_json, validate_dataset


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        dataset, checksum = read_json(args.dataset)
        manifest, _ = read_json(args.manifest)
        result = validate_dataset(dataset, manifest, checksum)
    except (ContentValidationError, OSError) as exc:
        message = str(exc) if isinstance(exc, ContentValidationError) else "Unable to read validation input"
        print(json.dumps({"structural_status": "failed", "message": message, "release_ready": False}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
