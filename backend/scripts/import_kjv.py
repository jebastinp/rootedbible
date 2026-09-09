"""Legacy network importer retired by the Rooted content-licensing workflow.

No translation is an automatic substitute for the owner's requested editions.
Use validate_bible.py to validate an approved local canonical source and manifest.
Promotion into the application additionally requires written rights and human QA.
"""


def import_kjv():
    raise SystemExit(
        "Automatic KJV download/import is disabled. No approved Rooted source or "
        "license evidence has been supplied. See docs/rooted/07-bible-licensing.md "
        "and docs/rooted/08-bible-data-schema.md before importing any Bible text."
    )


if __name__ == "__main__":
    import_kjv()
