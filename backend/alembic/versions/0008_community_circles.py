"""private, relationship-based community: family / buddy / church_challenge

Revision ID: 0008_community_circles
Revises: 0007_bible_verses_and_engagement
Create Date: 2026-09-09 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0008_community_circles"
down_revision = "0007_bible_verses_and_engagement"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "community",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("join_code", sa.String(10), nullable=False, unique=True),
        sa.Column("max_members", sa.Integer, nullable=True),
        sa.Column("reading_plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reading_plan.id", ondelete="SET NULL"), nullable=True),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("type in ('family','buddy','church_challenge')", name="chk_community_type"),
    )
    op.create_index("idx_community_owner", "community", ["owner_id"])

    op.create_table(
        "community_member",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("community_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("community.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(10), nullable=False, server_default="member"),
        sa.Column("status", sa.String(10), nullable=False, server_default="active"),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("community_id", "user_id", name="uq_community_member_once"),
        sa.CheckConstraint("role in ('owner','admin','member')", name="chk_member_role"),
        sa.CheckConstraint("status in ('active','removed','left')", name="chk_member_status"),
    )
    op.create_index("idx_member_community", "community_member", ["community_id"])
    op.create_index("idx_member_user", "community_member", ["user_id"])

    op.create_table(
        "community_join_request",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("community_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("community.id", ondelete="CASCADE"), nullable=False),
        sa.Column("requester_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("status", sa.String(10), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("responded_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("status in ('pending','accepted','declined','cancelled')", name="chk_request_status"),
    )
    op.create_index("idx_request_community", "community_join_request", ["community_id"])
    op.create_index("idx_request_target", "community_join_request", ["target_user_id"])
    op.create_index("idx_request_requester", "community_join_request", ["requester_id"])


def downgrade() -> None:
    op.drop_index("idx_request_requester", table_name="community_join_request")
    op.drop_index("idx_request_target", table_name="community_join_request")
    op.drop_index("idx_request_community", table_name="community_join_request")
    op.drop_table("community_join_request")

    op.drop_index("idx_member_user", table_name="community_member")
    op.drop_index("idx_member_community", table_name="community_member")
    op.drop_table("community_member")

    op.drop_index("idx_community_owner", table_name="community")
    op.drop_table("community")
