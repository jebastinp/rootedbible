import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.notes import Note, Highlight
from app.schemas.notes import NoteCreate, NoteUpdate, HighlightCreate


class NotesService:
    def __init__(self, db: Session):
        self.db = db

    # -- Notes --------------------------------------------------------
    def list_notes(self, user_id: uuid.UUID) -> list[Note]:
        return self.db.query(Note).filter(Note.user_id == user_id).order_by(Note.created_at.desc()).all()

    def create_note(self, user_id: uuid.UUID, payload: NoteCreate) -> Note:
        note = Note(
            user_id=user_id,
            verse_reference=payload.verse_reference,
            verse_id=payload.verse_id,
            translation_id=payload.translation_id,
            note_text=payload.note_text,
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def update_note(self, user_id: uuid.UUID, note_id: uuid.UUID, payload: NoteUpdate) -> Note:
        note = self.db.query(Note).filter(Note.id == note_id).first()
        if not note:
            raise NotFoundError("Note not found")
        if note.user_id != user_id:
            raise ForbiddenError("You can only edit your own notes")
        note.note_text = payload.note_text
        self.db.commit()
        self.db.refresh(note)
        return note

    def delete_note(self, user_id: uuid.UUID, note_id: uuid.UUID) -> None:
        note = self.db.query(Note).filter(Note.id == note_id).first()
        if not note:
            raise NotFoundError("Note not found")
        if note.user_id != user_id:
            raise ForbiddenError("You can only delete your own notes")
        self.db.delete(note)
        self.db.commit()

    def notes_for_chapter(self, user_id: uuid.UUID, verse_ids: list[uuid.UUID]) -> list[Note]:
        if not verse_ids:
            return []
        return self.db.query(Note).filter(Note.user_id == user_id, Note.verse_id.in_(verse_ids)).all()

    # -- Highlights -----------------------------------------------------
    def list_highlights(self, user_id: uuid.UUID) -> list[Highlight]:
        return self.db.query(Highlight).filter(Highlight.user_id == user_id).order_by(Highlight.created_at.desc()).all()

    def create_highlight(self, user_id: uuid.UUID, payload: HighlightCreate) -> Highlight:
        existing = (
            self.db.query(Highlight)
            .filter(Highlight.user_id == user_id, Highlight.verse_reference == payload.verse_reference)
            .first()
        )
        if existing:
            existing.color = payload.color
            existing.verse_id = payload.verse_id
            existing.translation_id = payload.translation_id
            existing.verse_start = payload.verse_start
            existing.verse_end = payload.verse_end
            self.db.commit()
            self.db.refresh(existing)
            return existing
        highlight = Highlight(
            user_id=user_id,
            verse_reference=payload.verse_reference,
            color=payload.color,
            verse_id=payload.verse_id,
            translation_id=payload.translation_id,
            verse_start=payload.verse_start,
            verse_end=payload.verse_end,
        )
        self.db.add(highlight)
        self.db.commit()
        self.db.refresh(highlight)
        return highlight

    def delete_highlight(self, user_id: uuid.UUID, highlight_id: uuid.UUID) -> None:
        highlight = self.db.query(Highlight).filter(Highlight.id == highlight_id).first()
        if not highlight:
            raise NotFoundError("Highlight not found")
        if highlight.user_id != user_id:
            raise ForbiddenError("You can only delete your own highlights")
        self.db.delete(highlight)
        self.db.commit()

    def highlights_for_chapter(self, user_id: uuid.UUID, verse_ids: list[uuid.UUID]) -> list[Highlight]:
        if not verse_ids:
            return []
        return self.db.query(Highlight).filter(Highlight.user_id == user_id, Highlight.verse_id.in_(verse_ids)).all()
