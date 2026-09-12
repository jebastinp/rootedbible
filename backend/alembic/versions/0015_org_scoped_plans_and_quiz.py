"""per-org reading plan calendars + quiz banks, member active-calendar
selection

Revision ID: 0015_org_scoped_plans_and_quiz
Revises: 0014_fellowship_code
Create Date: 2026-09-12 01:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0015_org_scoped_plans_and_quiz"
down_revision = "0014_fellowship_code"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- reading_plan: scope to platform / a Church / a Fellowship ---
    op.add_column("reading_plan", sa.Column("scope_key", sa.String(80), nullable=False, server_default="platform"))
    op.add_column("reading_plan", sa.Column("church_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("church.id", ondelete="CASCADE"), nullable=True))
    op.add_column("reading_plan", sa.Column("fellowship_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fellowship.id", ondelete="CASCADE"), nullable=True))
    op.alter_column("reading_plan", "scope_key", server_default=None)

    op.drop_constraint("reading_plan_day_number_key", "reading_plan", type_="unique")
    op.drop_constraint("reading_plan_reading_date_key", "reading_plan", type_="unique")
    op.create_unique_constraint("uq_reading_plan_scope_day", "reading_plan", ["scope_key", "day_number"])
    op.create_unique_constraint("uq_reading_plan_scope_date", "reading_plan", ["scope_key", "reading_date"])
    op.create_check_constraint("chk_reading_plan_one_scope", "reading_plan", "not (church_id is not null and fellowship_id is not null)")

    # --- quiz_question: optional per-org quiz bank ---
    op.add_column("quiz_question", sa.Column("church_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("church.id", ondelete="CASCADE"), nullable=True))
    op.add_column("quiz_question", sa.Column("fellowship_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fellowship.id", ondelete="CASCADE"), nullable=True))
    op.create_check_constraint("chk_quiz_question_one_scope", "quiz_question", "not (church_id is not null and fellowship_id is not null)")

    # --- quiz_attempt: which org's bank the attempt was drawn from ---
    op.add_column("quiz_attempt", sa.Column("church_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("church.id", ondelete="SET NULL"), nullable=True))
    op.add_column("quiz_attempt", sa.Column("fellowship_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fellowship.id", ondelete="SET NULL"), nullable=True))
    op.create_check_constraint("chk_quiz_attempt_one_scope", "quiz_attempt", "not (church_id is not null and fellowship_id is not null)")

    # --- users: which org's calendar/quiz bank this member follows ---
    op.add_column("users", sa.Column("active_calendar_church_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("church.id", ondelete="SET NULL"), nullable=True))
    op.add_column("users", sa.Column("active_calendar_fellowship_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fellowship.id", ondelete="SET NULL"), nullable=True))
    op.create_check_constraint("chk_user_one_active_calendar", "users", "not (active_calendar_church_id is not null and active_calendar_fellowship_id is not null)")


def downgrade() -> None:
    op.drop_constraint("chk_user_one_active_calendar", "users", type_="check")
    op.drop_column("users", "active_calendar_fellowship_id")
    op.drop_column("users", "active_calendar_church_id")

    op.drop_constraint("chk_quiz_attempt_one_scope", "quiz_attempt", type_="check")
    op.drop_column("quiz_attempt", "fellowship_id")
    op.drop_column("quiz_attempt", "church_id")

    op.drop_constraint("chk_quiz_question_one_scope", "quiz_question", type_="check")
    op.drop_column("quiz_question", "fellowship_id")
    op.drop_column("quiz_question", "church_id")

    op.drop_constraint("uq_reading_plan_scope_date", "reading_plan", type_="unique")
    op.drop_constraint("uq_reading_plan_scope_day", "reading_plan", type_="unique")
    op.drop_constraint("chk_reading_plan_one_scope", "reading_plan", type_="check")
    op.create_unique_constraint("reading_plan_day_number_key", "reading_plan", ["day_number"])
    op.create_unique_constraint("reading_plan_reading_date_key", "reading_plan", ["reading_date"])
    op.drop_column("reading_plan", "fellowship_id")
    op.drop_column("reading_plan", "church_id")
    op.drop_column("reading_plan", "scope_key")
