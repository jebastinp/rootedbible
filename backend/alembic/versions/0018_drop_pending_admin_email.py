"""Remove pending_admin_email - the final architecture has no "pending
invite" state; admin assignment resolves immediately against an existing
Rooted member or fails clearly (see AdminOrganizationAssignment,
introduced in 0017).

Revision ID: 0018_drop_pending_admin_email
Revises: 0017_admin_org_assignments
Create Date: 2026-09-13 00:30:00

"""
from alembic import op
import sqlalchemy as sa

revision = "0018_drop_pending_admin_email"
down_revision = "0017_admin_org_assignments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("church", "pending_admin_email")
    op.drop_column("fellowship", "pending_admin_email")


def downgrade() -> None:
    op.add_column("fellowship", sa.Column("pending_admin_email", sa.String(255), nullable=True))
    op.add_column("church", sa.Column("pending_admin_email", sa.String(255), nullable=True))
