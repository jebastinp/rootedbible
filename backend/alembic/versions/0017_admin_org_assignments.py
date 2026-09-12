"""Final 3-role architecture: drop the unused 'leader' role, and introduce
admin_organization_assignments as the single source of truth for which
Church or Fellowship an ADMIN manages. Backfills from the current
ChurchMember/FellowshipMember 'owner' rows so existing org owners become
real ADMIN accounts instead of staying role='member'.

Revision ID: 0017_admin_organization_assignments
Revises: 0016_pending_admin_email
Create Date: 2026-09-13 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0017_admin_org_assignments"
down_revision = "0016_pending_admin_email"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # --- 1. Recreate the user_role enum without 'leader' (safety first:
    # migrate any existing 'leader' rows to 'member' before the type is
    # swapped, since nothing in the new architecture uses that value). ---
    conn.execute(sa.text("update users set role = 'member' where role = 'leader'"))

    op.execute("ALTER TYPE user_role RENAME TO user_role_old")
    op.execute("CREATE TYPE user_role AS ENUM ('member', 'admin', 'super_admin')")
    op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE user_role USING role::text::user_role")
    op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'member'::user_role")
    op.execute("DROP TYPE user_role_old")

    # --- 2. admin_organization_assignments ---
    op.create_table(
        "admin_organization_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_type", sa.String(20), nullable=False),
        sa.Column("church_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("church.id", ondelete="CASCADE"), nullable=True),
        sa.Column("fellowship_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fellowship.id", ondelete="CASCADE"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("organization_type in ('church','fellowship')", name="chk_admin_assignment_org_type"),
        sa.CheckConstraint(
            "(organization_type = 'church' and church_id is not null and fellowship_id is null) "
            "or (organization_type = 'fellowship' and fellowship_id is not null and church_id is null)",
            name="chk_admin_assignment_org_matches_id",
        ),
        sa.UniqueConstraint("user_id", name="uq_admin_assignment_user"),
        sa.UniqueConstraint("church_id", name="uq_admin_assignment_church"),
        sa.UniqueConstraint("fellowship_id", name="uq_admin_assignment_fellowship"),
    )

    # --- 3. Backfill: each Church/Fellowship's current 'owner' member
    # becomes a real ADMIN with an assignment row. If a user happens to
    # own more than one org (shouldn't normally happen, but the old model
    # didn't forbid it), only the earliest-created org wins the migration -
    # Super Admin can reassign the rest afterward via the app. Never
    # touches an existing super_admin's role. ---
    church_owners = conn.execute(sa.text(
        "select cm.user_id, cm.church_id from church_member cm "
        "join church c on c.id = cm.church_id "
        "where cm.role = 'owner' and cm.status = 'active' "
        "order by c.created_at asc"
    )).fetchall()
    fellowship_owners = conn.execute(sa.text(
        "select fm.user_id, fm.fellowship_id from fellowship_member fm "
        "join fellowship f on f.id = fm.fellowship_id "
        "where fm.role = 'owner' and fm.status = 'active' "
        "order by f.created_at asc"
    )).fetchall()

    assigned_users: set = set()

    for user_id, church_id in church_owners:
        if user_id in assigned_users:
            continue
        role = conn.execute(sa.text("select role from users where id = :id"), {"id": user_id}).scalar()
        if role == "super_admin":
            continue
        conn.execute(sa.text(
            "insert into admin_organization_assignments (id, user_id, organization_type, church_id, fellowship_id) "
            "values (uuid_generate_v4(), :user_id, 'church', :church_id, null)"
        ), {"user_id": user_id, "church_id": church_id})
        conn.execute(sa.text("update users set role = 'admin' where id = :id"), {"id": user_id})
        assigned_users.add(user_id)

    for user_id, fellowship_id in fellowship_owners:
        if user_id in assigned_users:
            continue
        role = conn.execute(sa.text("select role from users where id = :id"), {"id": user_id}).scalar()
        if role == "super_admin":
            continue
        conn.execute(sa.text(
            "insert into admin_organization_assignments (id, user_id, organization_type, church_id, fellowship_id) "
            "values (uuid_generate_v4(), :user_id, 'fellowship', null, :fellowship_id)"
        ), {"user_id": user_id, "fellowship_id": fellowship_id})
        conn.execute(sa.text("update users set role = 'admin' where id = :id"), {"id": user_id})
        assigned_users.add(user_id)


def downgrade() -> None:
    op.drop_table("admin_organization_assignments")

    op.execute("ALTER TYPE user_role RENAME TO user_role_old")
    op.execute("CREATE TYPE user_role AS ENUM ('member', 'leader', 'admin', 'super_admin')")
    op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE user_role USING role::text::user_role")
    op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'member'::user_role")
    op.execute("DROP TYPE user_role_old")
