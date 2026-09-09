"""verse-level Bible storage, bookmarks, reading position/completion, note+highlight verse linkage

Revision ID: 0007_bible_verses_and_engagement
Revises: 0006_auth_provider_last_login
Create Date: 2026-09-09 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0007_bible_verses_and_engagement"
down_revision = "0006_auth_provider_last_login"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("bible_chapter", "text")

    op.create_table(
        "bible_verse",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bible_chapter.id", ondelete="CASCADE"), nullable=False),
        sa.Column("verse_number", sa.Integer, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.UniqueConstraint("chapter_id", "verse_number", name="uq_verse_per_chapter"),
    )
    op.create_index("idx_verse_chapter", "bible_verse", ["chapter_id"])

    op.create_table(
        "bookmark",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("verse_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bible_verse.id", ondelete="CASCADE"), nullable=False),
        sa.Column("translation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bible_version.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "verse_id", name="uq_bookmark_user_verse"),
    )
    op.create_index("idx_bookmark_user", "bookmark", ["user_id"])

    op.create_table(
        "reading_position",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("translation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bible_version.id", ondelete="CASCADE"), nullable=False),
        sa.Column("book_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bible_book.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chapter_number", sa.Integer, nullable=False),
        sa.Column("verse_number", sa.Integer, nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "reading_completion",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("translation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bible_version.id", ondelete="CASCADE"), nullable=False),
        sa.Column("book_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bible_book.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chapter_number", sa.Integer, nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "translation_id", "book_id", "chapter_number", name="uq_completion_once"),
    )
    op.create_index("idx_completion_user", "reading_completion", ["user_id"])

    op.add_column("note", sa.Column("verse_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bible_verse.id", ondelete="CASCADE"), nullable=True))
    op.add_column("note", sa.Column("translation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bible_version.id", ondelete="CASCADE"), nullable=True))
    op.add_column("note", sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))

    op.add_column("highlight", sa.Column("verse_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bible_verse.id", ondelete="CASCADE"), nullable=True))
    op.add_column("highlight", sa.Column("translation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bible_version.id", ondelete="CASCADE"), nullable=True))
    op.add_column("highlight", sa.Column("verse_start", sa.Integer, nullable=True))
    op.add_column("highlight", sa.Column("verse_end", sa.Integer, nullable=True))
    op.add_column("highlight", sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))


def downgrade() -> None:
    op.drop_column("highlight", "updated_at")
    op.drop_column("highlight", "verse_end")
    op.drop_column("highlight", "verse_start")
    op.drop_column("highlight", "translation_id")
    op.drop_column("highlight", "verse_id")

    op.drop_column("note", "updated_at")
    op.drop_column("note", "translation_id")
    op.drop_column("note", "verse_id")

    op.drop_index("idx_completion_user", table_name="reading_completion")
    op.drop_table("reading_completion")
    op.drop_table("reading_position")
    op.drop_index("idx_bookmark_user", table_name="bookmark")
    op.drop_table("bookmark")
    op.drop_index("idx_verse_chapter", table_name="bible_verse")
    op.drop_table("bible_verse")

    op.add_column("bible_chapter", sa.Column("text", sa.Text, nullable=False, server_default=""))
