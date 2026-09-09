"""bible content, quiz, notes and highlights

Revision ID: 0002_bible_quiz_notes
Revises: 0001_initial
Create Date: 2026-09-08 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_bible_quiz_notes"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bible_version",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("language", sa.String(40), nullable=False),
        sa.Column("version_name", sa.String(120), nullable=False),
        sa.Column("license_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "bible_book",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("bible_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bible_version.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(60), nullable=False),
        sa.Column("testament", sa.String(3), nullable=False),
        sa.Column("sort_order", sa.Integer, nullable=False),
        sa.Column("chapter_count", sa.Integer, nullable=False),
        sa.UniqueConstraint("bible_version_id", "name", name="uq_book_per_version"),
        sa.CheckConstraint("testament in ('OT','NT')", name="chk_testament"),
    )

    op.create_table(
        "bible_chapter",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("book_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bible_book.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chapter_number", sa.Integer, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.UniqueConstraint("book_id", "chapter_number", name="uq_chapter_per_book"),
    )
    op.create_index("idx_bible_chapter_book", "bible_chapter", ["book_id"])

    op.create_table(
        "quiz_question",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bible_chapter.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("options", postgresql.JSONB, nullable=False),
        sa.Column("correct_index", sa.Integer, nullable=False),
        sa.Column("verse_reference", sa.String(60), nullable=False),
        sa.Column("age_group", sa.String(10), nullable=False, server_default="adult"),
    )
    op.create_index("idx_quiz_question_chapter", "quiz_question", ["chapter_id"])

    op.create_table(
        "quiz_attempt",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reading_plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reading_plan.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bible_chapter.id", ondelete="SET NULL"), nullable=True),
        sa.Column("score", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_questions", sa.Integer, nullable=False, server_default="0"),
        sa.Column("passed", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("attempt_count", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_quiz_attempt_user", "quiz_attempt", ["user_id", "reading_plan_id"])

    op.create_table(
        "note",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("verse_reference", sa.String(60), nullable=False),
        sa.Column("note_text", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_note_user", "note", ["user_id"])

    op.create_table(
        "highlight",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("verse_reference", sa.String(60), nullable=False),
        sa.Column("color", sa.String(10), nullable=False, server_default="yellow"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("color in ('yellow','blue','green','red','purple')", name="chk_highlight_color"),
    )
    op.create_index("idx_highlight_user", "highlight", ["user_id"])

    op.execute(
        """
        insert into bible_version (code, language, version_name, license_status)
        values
            ('kjv1769', 'English', 'King James Version (1769)', 'public_domain'),
            ('nkjv', 'English', 'New King James Version', 'pending'),
            ('ta_bsi', 'Tamil', 'Tamil Bible (Bible Society of India)', 'pending'),
            ('te_bsi', 'Telugu', 'Telugu Bible (Bible Society of India)', 'pending'),
            ('kn_bsi', 'Kannada', 'Kannada Bible (Bible Society of India)', 'pending'),
            ('hi_bsi', 'Hindi', 'Hindi Bible (Bible Society of India)', 'pending')
        on conflict (code) do nothing
        """
    )


def downgrade() -> None:
    op.drop_table("highlight")
    op.drop_table("note")
    op.drop_table("quiz_attempt")
    op.drop_table("quiz_question")
    op.drop_table("bible_chapter")
    op.drop_table("bible_book")
    op.drop_table("bible_version")
