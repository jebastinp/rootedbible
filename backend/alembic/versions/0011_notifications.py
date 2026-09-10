"""notifications

Revision ID: 0011_notifications
Revises: 0010_standalone_community
Create Date: 2026-09-10 01:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0011_notifications"
down_revision = "0010_standalone_community"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notification",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(40), nullable=False),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("link", sa.String(300), nullable=True),
        sa.Column("is_read", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_notification_user", "notification", ["user_id"])
    op.create_index("idx_notification_user_unread", "notification", ["user_id", "is_read"])


def downgrade() -> None:
    op.drop_index("idx_notification_user_unread", table_name="notification")
    op.drop_index("idx_notification_user", table_name="notification")
    op.drop_table("notification")
