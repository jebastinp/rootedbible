import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    verse_reference: str = Field(max_length=60)
    note_text: str = Field(max_length=2000)
    verse_id: Optional[uuid.UUID] = None
    translation_id: Optional[uuid.UUID] = None


class NoteUpdate(BaseModel):
    note_text: str = Field(max_length=2000)


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    verse_reference: str
    verse_id: Optional[uuid.UUID] = None
    note_text: str
    created_at: datetime
    updated_at: datetime


class HighlightCreate(BaseModel):
    verse_reference: str = Field(max_length=60)
    color: str = Field(pattern="^(yellow|blue|green|red|purple)$")
    verse_id: Optional[uuid.UUID] = None
    translation_id: Optional[uuid.UUID] = None
    verse_start: Optional[int] = None
    verse_end: Optional[int] = None


class HighlightOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    verse_reference: str
    color: str
    verse_id: Optional[uuid.UUID] = None
    verse_start: Optional[int] = None
    verse_end: Optional[int] = None
    created_at: datetime
