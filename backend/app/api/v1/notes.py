import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.notes import NoteCreate, NoteUpdate, NoteOut, HighlightCreate, HighlightOut
from app.services.notes_service import NotesService

router = APIRouter(prefix="/notes", tags=["Notes & Highlights"])


@router.get("", response_model=list[NoteOut], summary="List my notes")
def list_notes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return NotesService(db).list_notes(current_user.id)


@router.post("", response_model=NoteOut, summary="Add a note to a verse")
def create_note(payload: NoteCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return NotesService(db).create_note(current_user.id, payload)


@router.patch("/{note_id}", response_model=NoteOut, summary="Edit my own note")
def update_note(note_id: uuid.UUID, payload: NoteUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return NotesService(db).update_note(current_user.id, note_id, payload)


@router.delete("/{note_id}", summary="Delete my own note")
def delete_note(note_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    NotesService(db).delete_note(current_user.id, note_id)
    return {"success": True}


@router.get("/highlights", response_model=list[HighlightOut], summary="List my highlights")
def list_highlights(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return NotesService(db).list_highlights(current_user.id)


@router.post("/highlights", response_model=HighlightOut, summary="Highlight a verse (or change its color)")
def create_highlight(payload: HighlightCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return NotesService(db).create_highlight(current_user.id, payload)


@router.delete("/highlights/{highlight_id}", summary="Remove my own highlight")
def delete_highlight(highlight_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    NotesService(db).delete_highlight(current_user.id, highlight_id)
    return {"success": True}
