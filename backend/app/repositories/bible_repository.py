from sqlalchemy.orm import Session, joinedload

from app.models.bible import BibleVersion, BibleBook, BibleChapter, BibleVerse
from app.content.licensing import approved_web_codes


class BibleRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_versions(self, only_visible: bool = True) -> list[BibleVersion]:
        query = self.db.query(BibleVersion).filter(BibleVersion.is_active.is_(True))
        if only_visible:
            # "pending" versions exist as placeholders in the schema but are
            # never shown to users until an admin marks them licensed.
            query = query.filter(
                BibleVersion.license_status.in_(["public_domain", "licensed"]),
                BibleVersion.code.in_(approved_web_codes()),
            )
        return query.order_by(BibleVersion.language.asc()).all()

    def get_version_by_code(self, code: str) -> BibleVersion | None:
        if code not in approved_web_codes():
            return None
        return self.db.query(BibleVersion).filter(
            BibleVersion.code == code,
            BibleVersion.is_active.is_(True),
            BibleVersion.license_status.in_(["public_domain", "licensed"]),
        ).first()

    def list_books(self, version_id) -> list[BibleBook]:
        return (
            self.db.query(BibleBook)
            .filter(BibleBook.bible_version_id == version_id)
            .order_by(BibleBook.sort_order.asc())
            .all()
        )

    def get_book_by_name(self, version_id, name: str) -> BibleBook | None:
        return (
            self.db.query(BibleBook)
            .filter(BibleBook.bible_version_id == version_id, BibleBook.name.ilike(name))
            .first()
        )

    def get_chapter(self, book_id, chapter_number: int) -> BibleChapter | None:
        return (
            self.db.query(BibleChapter)
            .options(joinedload(BibleChapter.verses))
            .filter(BibleChapter.book_id == book_id, BibleChapter.chapter_number == chapter_number)
            .first()
        )

    def get_verse(self, verse_id) -> BibleVerse | None:
        return self.db.query(BibleVerse).filter(BibleVerse.id == verse_id).first()

    def search_verses(self, version_id, query: str, limit: int = 50) -> list[BibleVerse]:
        like = f"%{query}%"
        return (
            self.db.query(BibleVerse)
            .join(BibleChapter, BibleChapter.id == BibleVerse.chapter_id)
            .join(BibleBook, BibleBook.id == BibleChapter.book_id)
            .options(joinedload(BibleVerse.chapter).joinedload(BibleChapter.book))
            .filter(BibleBook.bible_version_id == version_id, BibleVerse.text.ilike(like))
            .order_by(BibleBook.sort_order.asc(), BibleChapter.chapter_number.asc(), BibleVerse.verse_number.asc())
            .limit(limit)
            .all()
        )
