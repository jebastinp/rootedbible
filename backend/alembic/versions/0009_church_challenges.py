"""church challenge as the parent for family / buddy community groups

Revision ID: 0009_church_challenges
Revises: 0008_community_circles
Create Date: 2026-09-09 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0009_church_challenges"
down_revision = "0008_community_circles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("community_join_request")
    op.drop_table("community_member")
    op.drop_table("community")

    op.create_table(
        "church_challenge",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("church_name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("reading_plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reading_plan.id", ondelete="SET NULL"), nullable=True),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("participant_limit", sa.Integer, nullable=False, server_default="100"),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("allow_families", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("family_limit", sa.Integer, nullable=False, server_default="4"),
        sa.Column("allow_buddies", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("buddy_limit", sa.Integer, nullable=False, server_default="5"),
        sa.Column("quiz_enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("rewards_enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status in ('draft','active','completed','archived')", name="chk_challenge_status"),
    )

    op.create_table(
        "challenge_member",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("challenge_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("church_challenge.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("role", sa.String(20), nullable=False, server_default="participant"),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("challenge_id", "user_id", name="uq_challenge_member_once"),
        sa.CheckConstraint("status in ('pending','active','removed')", name="chk_challenge_member_status"),
        sa.CheckConstraint("role in ('participant','admin')", name="chk_challenge_member_role"),
    )
    op.create_index("idx_challenge_member_challenge", "challenge_member", ["challenge_id"])
    op.create_index("idx_challenge_member_user", "challenge_member", ["user_id"])

    op.create_table(
        "family",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("challenge_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("church_challenge.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_family_challenge", "family", ["challenge_id"])

    op.create_table(
        "family_member",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("family_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("family.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(10), nullable=False, server_default="member"),
        sa.Column("status", sa.String(10), nullable=False, server_default="active"),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("family_id", "user_id", name="uq_family_member_once"),
        sa.CheckConstraint("role in ('owner','member')", name="chk_family_member_role"),
        sa.CheckConstraint("status in ('active','removed','left')", name="chk_family_member_status"),
    )
    op.create_index("idx_family_member_family", "family_member", ["family_id"])
    op.create_index("idx_family_member_user", "family_member", ["user_id"])

    op.create_table(
        "buddy_group",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("challenge_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("church_challenge.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_buddy_group_challenge", "buddy_group", ["challenge_id"])

    op.create_table(
        "buddy_member",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("buddy_group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buddy_group.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(10), nullable=False, server_default="member"),
        sa.Column("status", sa.String(10), nullable=False, server_default="active"),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("buddy_group_id", "user_id", name="uq_buddy_member_once"),
        sa.CheckConstraint("role in ('owner','member')", name="chk_buddy_member_role"),
        sa.CheckConstraint("status in ('active','removed','left')", name="chk_buddy_member_status"),
    )
    op.create_index("idx_buddy_member_group", "buddy_member", ["buddy_group_id"])
    op.create_index("idx_buddy_member_user", "buddy_member", ["user_id"])

    op.create_table(
        "join_request",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("requester_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("challenge_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("church_challenge.id", ondelete="CASCADE"), nullable=True),
        sa.Column("family_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("family.id", ondelete="CASCADE"), nullable=True),
        sa.Column("buddy_group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buddy_group.id", ondelete="CASCADE"), nullable=True),
        sa.Column("status", sa.String(10), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("responded_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.CheckConstraint("type in ('challenge','family','buddy')", name="chk_request_type"),
        sa.CheckConstraint("status in ('pending','approved','declined','cancelled')", name="chk_request_status"),
    )
    op.create_index("idx_request_requester", "join_request", ["requester_id"])
    op.create_index("idx_request_target", "join_request", ["target_user_id"])
    op.create_index("idx_request_challenge", "join_request", ["challenge_id"])
    op.create_index("idx_request_family", "join_request", ["family_id"])
    op.create_index("idx_request_buddy_group", "join_request", ["buddy_group_id"])

    op.create_table(
        "challenge_reward",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("challenge_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("church_challenge.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("requirement_type", sa.String(20), nullable=False),
        sa.Column("requirement_value", sa.Integer, nullable=False),
        sa.Column("badge_icon", sa.String(40), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("requirement_type in ('streak','completion')", name="chk_reward_requirement_type"),
    )
    op.create_index("idx_reward_challenge", "challenge_reward", ["challenge_id"])

    op.create_table(
        "encouragement",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("from_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("to_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("family_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("family.id", ondelete="CASCADE"), nullable=True),
        sa.Column("buddy_group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buddy_group.id", ondelete="CASCADE"), nullable=True),
        sa.Column("message", sa.String(120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "(family_id is not null and buddy_group_id is null) or (family_id is null and buddy_group_id is not null)",
            name="chk_encouragement_one_scope",
        ),
    )
    op.create_index("idx_encouragement_family", "encouragement", ["family_id"])
    op.create_index("idx_encouragement_buddy_group", "encouragement", ["buddy_group_id"])


def downgrade() -> None:
    op.drop_table("encouragement")
    op.drop_table("challenge_reward")
    op.drop_table("join_request")
    op.drop_table("buddy_member")
    op.drop_table("buddy_group")
    op.drop_table("family_member")
    op.drop_table("family")
    op.drop_table("challenge_member")
    op.drop_table("church_challenge")

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
    op.create_table(
        "community_member",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("community_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("community.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(10), nullable=False, server_default="member"),
        sa.Column("status", sa.String(10), nullable=False, server_default="active"),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("community_id", "user_id", name="uq_community_member_once"),
    )
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
    )
