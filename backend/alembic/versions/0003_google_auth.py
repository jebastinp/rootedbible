"""add google sign-in columns to users

Revision ID: 0003_google_auth
Revises: 0002_bible_quiz_notes
Create Date: 2026-09-09 00:00:00

"""
from alembic import op
import sqlalchemy as sa

revision = "0003_google_auth"
down_revision = "0002_bible_quiz_notes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("google_sub", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("email", sa.String(255), nullable=True))
    op.create_unique_constraint("uq_users_google_sub", "users", ["google_sub"])
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.create_index("ix_users_google_sub", "users", ["google_sub"])
    op.create_index("ix_users_email", "users", ["email"])


def downgrade() -> None:
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_google_sub", table_name="users")
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.drop_constraint("uq_users_google_sub", "users", type_="unique")
    op.drop_column("users", "email")
    op.drop_column("users", "google_sub")
