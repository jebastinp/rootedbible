"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # create_type=False: the type is created explicitly below via .create()
    # so op.create_table() must NOT also try to auto-create it - passing an
    # ENUM with the (SQLAlchemy) default create_type=True as a column type
    # makes create_table() emit its own CREATE TYPE, colliding with the one
    # just created and failing with "type already exists".
    user_role = postgresql.ENUM("member", "leader", "admin", "super_admin", name="user_role", create_type=False)
    user_status = postgresql.ENUM("active", "inactive", "suspended", name="user_status", create_type=False)
    announcement_visibility = postgresql.ENUM("all", "members", "leaders", "admins", name="announcement_visibility", create_type=False)
    import_status = postgresql.ENUM("pending", "processing", "success", "failed", "rolled_back", name="import_status", create_type=False)

    bind = op.get_bind()
    user_role.create(bind, checkfirst=True)
    user_status.create(bind, checkfirst=True)
    announcement_visibility.create(bind, checkfirst=True)
    import_status.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", sa.String(20), nullable=False, unique=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("role", user_role, nullable=False, server_default="member"),
        sa.Column("status", user_status, nullable=False, server_default="active"),
        sa.Column("photo_url", sa.Text(), nullable=True),
        sa.Column("joined_date", sa.Date(), nullable=False, server_default=sa.text("CURRENT_DATE")),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_users_user_id", "users", ["user_id"])
    op.create_index("idx_users_role", "users", ["role"])

    op.create_table(
        "reading_plan",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("day_number", sa.Integer(), nullable=False, unique=True),
        sa.Column("reading_date", sa.Date(), nullable=False, unique=True),
        sa.Column("old_testament", sa.Text(), nullable=True),
        sa.Column("new_testament", sa.Text(), nullable=True),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("day_number > 0", name="chk_day_number_positive"),
    )
    op.create_index("idx_reading_plan_date", "reading_plan", ["reading_date"])

    op.create_table(
        "reading_progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reading_plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reading_plan.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day_number", sa.Integer(), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", "reading_plan_id", name="uq_user_plan"),
    )
    op.create_index("idx_progress_user", "reading_progress", ["user_id"])
    op.create_index("idx_progress_plan", "reading_progress", ["reading_plan_id"])

    op.create_table(
        "user_stats",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("current_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("longest_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("days_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ot_days_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("nt_days_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("overall_percentage", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("last_completed_date", sa.Date(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "announcements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("publish_date", sa.Date(), nullable=False, server_default=sa.text("CURRENT_DATE")),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("visibility", announcement_visibility, nullable=False, server_default="all"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "church_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("church_name", sa.String(200), nullable=False, server_default="Rooted Church"),
        sa.Column("church_logo_url", sa.Text(), nullable=True),
        sa.Column("reading_year", sa.Integer(), nullable=False, server_default="2026"),
        sa.Column("verse_of_the_day", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_audit_created", "audit_logs", ["created_at"])

    op.create_table(
        "import_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("file_type", sa.String(30), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("status", import_status, nullable=False, server_default="pending"),
        sa.Column("total_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("inserted_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("skipped_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_log", postgresql.JSONB(), nullable=True),
        sa.Column("imported_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("import_history")
    op.drop_table("audit_logs")
    op.drop_table("church_settings")
    op.drop_table("announcements")
    op.drop_table("user_stats")
    op.drop_table("reading_progress")
    op.drop_table("reading_plan")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS import_status")
    op.execute("DROP TYPE IF EXISTS announcement_visibility")
    op.execute("DROP TYPE IF EXISTS user_status")
    op.execute("DROP TYPE IF EXISTS user_role")
