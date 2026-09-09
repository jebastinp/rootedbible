"""switch sign-in identity column from google_sub to supabase_user_id

Google sign-in is now handled by Supabase Auth (frontend uses supabase-js'
signInWithOAuth, backend verifies the resulting Supabase session JWT) instead
of verifying a Google ID token directly. The identity we store per user is
therefore the Supabase auth user id, not Google's own "sub" claim.

Revision ID: 0005_supabase_auth
Revises: 0004_reading_plan_passages
Create Date: 2026-09-09 00:00:00

"""
from alembic import op

revision = "0005_supabase_auth"
down_revision = "0004_reading_plan_passages"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_users_google_sub", table_name="users")
    op.drop_constraint("uq_users_google_sub", "users", type_="unique")
    op.alter_column("users", "google_sub", new_column_name="supabase_user_id")
    op.create_unique_constraint("uq_users_supabase_user_id", "users", ["supabase_user_id"])
    op.create_index("ix_users_supabase_user_id", "users", ["supabase_user_id"])


def downgrade() -> None:
    op.drop_index("ix_users_supabase_user_id", table_name="users")
    op.drop_constraint("uq_users_supabase_user_id", "users", type_="unique")
    op.alter_column("users", "supabase_user_id", new_column_name="google_sub")
    op.create_unique_constraint("uq_users_google_sub", "users", ["google_sub"])
    op.create_index("ix_users_google_sub", "users", ["google_sub"])
