"""standalone Family/Buddy (no cap, optional challenge link), Church, Fellowship, Group, user address

Revision ID: 0010_standalone_community
Revises: 0009_church_challenges
Create Date: 2026-09-10 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0010_standalone_community"
down_revision = "0009_church_challenges"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- User: address fields ---
    op.add_column("users", sa.Column("house_no", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("street_name", sa.String(150), nullable=True))
    op.add_column("users", sa.Column("city_name", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("state_name", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("postcode", sa.String(20), nullable=True))
    op.add_column("users", sa.Column("country", sa.String(100), nullable=True))

    # --- Family / BuddyGroup: decouple from Church Challenge, drop cap columns ---
    op.alter_column("family", "challenge_id", nullable=True)
    op.drop_constraint("family_challenge_id_fkey", "family", type_="foreignkey")
    op.create_foreign_key("family_challenge_id_fkey", "family", "church_challenge", ["challenge_id"], ["id"], ondelete="SET NULL")
    op.add_column("family", sa.Column("privacy", sa.String(20), nullable=False, server_default="private"))

    op.alter_column("buddy_group", "challenge_id", nullable=True)
    op.drop_constraint("buddy_group_challenge_id_fkey", "buddy_group", type_="foreignkey")
    op.create_foreign_key("buddy_group_challenge_id_fkey", "buddy_group", "church_challenge", ["challenge_id"], ["id"], ondelete="SET NULL")
    op.add_column("buddy_group", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("buddy_group", sa.Column("privacy", sa.String(20), nullable=False, server_default="private"))

    op.drop_column("church_challenge", "family_limit")
    op.drop_column("church_challenge", "buddy_limit")
    op.alter_column("church_challenge", "participant_limit", nullable=True, server_default=None)

    # --- Church ---
    op.create_table(
        "church",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("church_code", sa.String(20), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("privacy", sa.String(20), nullable=False, server_default="public"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("status in ('active','suspended')", name="chk_church_status"),
        sa.CheckConstraint("privacy in ('public','private','invite_only')", name="chk_church_privacy"),
    )
    op.create_index("idx_church_owner", "church", ["owner_id"])

    op.create_table(
        "church_member",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("church_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("church.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(10), nullable=False, server_default="member"),
        sa.Column("status", sa.String(10), nullable=False, server_default="active"),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("church_id", "user_id", name="uq_church_member_once"),
        sa.CheckConstraint("role in ('owner','admin','member')", name="chk_church_member_role"),
        sa.CheckConstraint("status in ('active','removed','left')", name="chk_church_member_status"),
    )
    op.create_index("idx_church_member_church", "church_member", ["church_id"])
    op.create_index("idx_church_member_user", "church_member", ["user_id"])

    # --- Fellowship ---
    op.create_table(
        "fellowship",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("church_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("church.id", ondelete="SET NULL"), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("privacy", sa.String(20), nullable=False, server_default="public"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("status in ('active','suspended')", name="chk_fellowship_status"),
        sa.CheckConstraint("privacy in ('public','private','invite_only')", name="chk_fellowship_privacy"),
    )
    op.create_index("idx_fellowship_church", "fellowship", ["church_id"])
    op.create_index("idx_fellowship_owner", "fellowship", ["owner_id"])

    op.create_table(
        "fellowship_member",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("fellowship_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fellowship.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(10), nullable=False, server_default="member"),
        sa.Column("status", sa.String(10), nullable=False, server_default="active"),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("fellowship_id", "user_id", name="uq_fellowship_member_once"),
        sa.CheckConstraint("role in ('owner','admin','member')", name="chk_fellowship_member_role"),
        sa.CheckConstraint("status in ('active','removed','left')", name="chk_fellowship_member_status"),
    )
    op.create_index("idx_fellowship_member_fellowship", "fellowship_member", ["fellowship_id"])
    op.create_index("idx_fellowship_member_user", "fellowship_member", ["user_id"])

    # --- Rooted Group (Sunday / Blazer / Youth / Men / Women, expandable) ---
    op.create_table(
        "rooted_group",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "user_group_membership",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rooted_group.id", ondelete="CASCADE"), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "group_id", name="uq_user_group_once"),
    )
    op.create_index("idx_user_group_user", "user_group_membership", ["user_id"])

    op.execute(
        "INSERT INTO rooted_group (name, sort_order) VALUES "
        "('Sunday', 1), ('Blazer', 2), ('Youth', 3), ('Men', 4), ('Women', 5)"
    )

    # --- JoinRequest: widen to cover church/fellowship ---
    op.drop_constraint("chk_request_type", "join_request", type_="check")
    op.create_check_constraint("chk_request_type", "join_request", "type in ('challenge','family','buddy','church','fellowship')")
    op.add_column("join_request", sa.Column("church_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("church.id", ondelete="CASCADE"), nullable=True))
    op.add_column("join_request", sa.Column("fellowship_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fellowship.id", ondelete="CASCADE"), nullable=True))
    op.create_index("idx_request_church", "join_request", ["church_id"])
    op.create_index("idx_request_fellowship", "join_request", ["fellowship_id"])


def downgrade() -> None:
    op.drop_index("idx_request_fellowship", table_name="join_request")
    op.drop_index("idx_request_church", table_name="join_request")
    op.drop_column("join_request", "fellowship_id")
    op.drop_column("join_request", "church_id")
    op.drop_constraint("chk_request_type", "join_request", type_="check")
    op.create_check_constraint("chk_request_type", "join_request", "type in ('challenge','family','buddy')")

    op.drop_index("idx_user_group_user", table_name="user_group_membership")
    op.drop_table("user_group_membership")
    op.drop_table("rooted_group")

    op.drop_index("idx_fellowship_member_user", table_name="fellowship_member")
    op.drop_index("idx_fellowship_member_fellowship", table_name="fellowship_member")
    op.drop_table("fellowship_member")
    op.drop_index("idx_fellowship_owner", table_name="fellowship")
    op.drop_index("idx_fellowship_church", table_name="fellowship")
    op.drop_table("fellowship")

    op.drop_index("idx_church_member_user", table_name="church_member")
    op.drop_index("idx_church_member_church", table_name="church_member")
    op.drop_table("church_member")
    op.drop_index("idx_church_owner", table_name="church")
    op.drop_table("church")

    op.alter_column("church_challenge", "participant_limit", nullable=False, server_default="100")
    op.add_column("church_challenge", sa.Column("buddy_limit", sa.Integer, nullable=False, server_default="5"))
    op.add_column("church_challenge", sa.Column("family_limit", sa.Integer, nullable=False, server_default="4"))

    op.drop_column("buddy_group", "privacy")
    op.drop_column("buddy_group", "description")
    op.drop_constraint("buddy_group_challenge_id_fkey", "buddy_group", type_="foreignkey")
    op.create_foreign_key("buddy_group_challenge_id_fkey", "buddy_group", "church_challenge", ["challenge_id"], ["id"], ondelete="CASCADE")
    op.alter_column("buddy_group", "challenge_id", nullable=False)

    op.drop_column("family", "privacy")
    op.drop_constraint("family_challenge_id_fkey", "family", type_="foreignkey")
    op.create_foreign_key("family_challenge_id_fkey", "family", "church_challenge", ["challenge_id"], ["id"], ondelete="CASCADE")
    op.alter_column("family", "challenge_id", nullable=False)

    op.drop_column("users", "country")
    op.drop_column("users", "postcode")
    op.drop_column("users", "state_name")
    op.drop_column("users", "city_name")
    op.drop_column("users", "street_name")
    op.drop_column("users", "house_no")
