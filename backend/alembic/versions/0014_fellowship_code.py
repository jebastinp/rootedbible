"""add fellowship_code, mirroring Church's church_code join-by-code system

Revision ID: 0014_fellowship_code
Revises: 0013_sunday_school_rename
Create Date: 2026-09-12 00:00:00

"""
import secrets
import string

from alembic import op
import sqlalchemy as sa

revision = "0014_fellowship_code"
down_revision = "0013_sunday_school_rename"
branch_labels = None
depends_on = None

_CODE_ALPHABET = "".join(c for c in string.ascii_uppercase + string.digits if c not in "01OI")


def upgrade() -> None:
    op.add_column("fellowship", sa.Column("fellowship_code", sa.String(20), nullable=True))

    conn = op.get_bind()
    existing_codes = {row[0] for row in conn.execute(sa.text("select fellowship_code from fellowship where fellowship_code is not null"))}
    rows = conn.execute(sa.text("select id from fellowship")).fetchall()
    for (fellowship_id,) in rows:
        code = None
        for _ in range(20):
            candidate = "ROOTED-" + "".join(secrets.choice(_CODE_ALPHABET) for _ in range(6))
            if candidate not in existing_codes:
                code = candidate
                break
        if code is None:
            raise RuntimeError("Could not allocate a unique fellowship code")
        existing_codes.add(code)
        conn.execute(sa.text("update fellowship set fellowship_code = :code where id = :id"), {"code": code, "id": fellowship_id})

    op.alter_column("fellowship", "fellowship_code", nullable=False)
    op.create_unique_constraint("uq_fellowship_code", "fellowship", ["fellowship_code"])


def downgrade() -> None:
    op.drop_constraint("uq_fellowship_code", "fellowship", type_="unique")
    op.drop_column("fellowship", "fellowship_code")
