"""pre-provision a Church/Fellowship admin by email before they sign up

Revision ID: 0016_pending_admin_email
Revises: 0015_org_scoped_plans_and_quiz
Create Date: 2026-09-12 02:00:00

"""
from alembic import op
import sqlalchemy as sa

revision = "0016_pending_admin_email"
down_revision = "0015_org_scoped_plans_and_quiz"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("church", sa.Column("pending_admin_email", sa.String(255), nullable=True))
    op.add_column("fellowship", sa.Column("pending_admin_email", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("fellowship", "pending_admin_email")
    op.drop_column("church", "pending_admin_email")
