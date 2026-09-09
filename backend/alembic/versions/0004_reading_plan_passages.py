"""structured, validated bible references for reading plan days

Revision ID: 0004_reading_plan_passages
Revises: 0003_google_auth
Create Date: 2026-09-09 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_reading_plan_passages"
down_revision = "0003_google_auth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reading_plan_passage",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("reading_plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reading_plan.id", ondelete="CASCADE"), nullable=False),
        sa.Column("testament", sa.String(3), nullable=False),
        sa.Column("book_name", sa.String(60), nullable=False),
        sa.Column("chapter_start", sa.Integer, nullable=False),
        sa.Column("chapter_end", sa.Integer, nullable=False),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.CheckConstraint("testament in ('OT','NT')", name="chk_passage_testament"),
        sa.CheckConstraint("chapter_end >= chapter_start", name="chk_passage_chapter_range"),
    )
    op.create_index("idx_passage_plan", "reading_plan_passage", ["reading_plan_id"])


def downgrade() -> None:
    op.drop_index("idx_passage_plan", table_name="reading_plan_passage")
    op.drop_table("reading_plan_passage")
