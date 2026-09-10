"""leaderboard config

Revision ID: 0012_leaderboard_config
Revises: 0011_notifications
Create Date: 2026-09-10 02:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0012_leaderboard_config"
down_revision = "0011_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leaderboard_config",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("challenge_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("church_challenge.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scope", sa.String(40), nullable=False),
        sa.Column("ranking_limit", sa.Integer, nullable=False, server_default="3"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("challenge_id", "scope", name="uq_leaderboard_config_scope"),
    )
    op.create_index("idx_leaderboard_config_challenge", "leaderboard_config", ["challenge_id"])


def downgrade() -> None:
    op.drop_index("idx_leaderboard_config_challenge", table_name="leaderboard_config")
    op.drop_table("leaderboard_config")
