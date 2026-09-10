"""rename Sunday ministry group to Sunday School

Revision ID: 0013_sunday_school_rename
Revises: 0012_leaderboard_config
Create Date: 2026-09-11 00:00:00

"""
from alembic import op
import sqlalchemy as sa

revision = "0013_sunday_school_rename"
down_revision = "0012_leaderboard_config"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("update rooted_group set name = 'Sunday School' where name = 'Sunday'")


def downgrade() -> None:
    op.execute("update rooted_group set name = 'Sunday' where name = 'Sunday School'")
