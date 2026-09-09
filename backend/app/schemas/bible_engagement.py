import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BookmarkCreate(BaseModel):
    verse_id: uuid.UUID
    translation_id: uuid.UUID


class BookmarkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    verse_id: uuid.UUID
    translation_id: uuid.UUID
    book_name: str
    chapter_number: int
    verse_number: int
    verse_text: str
    created_at: datetime


class ReadingPositionSet(BaseModel):
    translation_id: uuid.UUID
    book_id: uuid.UUID
    chapter_number: int = Field(gt=0)
    verse_number: int = Field(default=1, gt=0)


class ReadingPositionOut(BaseModel):
    translation_code: str
    book_name: str
    chapter_number: int
    verse_number: int
    updated_at: datetime


class ReadingCompletionCreate(BaseModel):
    translation_id: uuid.UUID
    book_id: uuid.UUID
    chapter_number: int = Field(gt=0)


class ReadingCompletionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    translation_id: uuid.UUID
    book_id: uuid.UUID
    chapter_number: int
    completed_at: datetime
    already_completed: bool = False
