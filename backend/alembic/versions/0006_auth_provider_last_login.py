"""track how each account signed up and when it last logged in

Revision ID: 0006_auth_provider_last_login
Revises: 0005_supabase_auth
Create Date: 2026-09-09 00:00:00

"""
from alembic import op
import sqlalchemy as sa

revision = "0006_auth_provider_last_login"
down_revision = "0005_supabase_auth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("auth_provider", sa.String(20), nullable=True))
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "auth_provider")
