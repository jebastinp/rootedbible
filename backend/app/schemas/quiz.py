import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class QuizQuestionOut(BaseModel):
    """Never includes correct_index - that would let the client cheat."""
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question: str
    options: list[str]


class QuizForChapterOut(BaseModel):
    chapter_id: uuid.UUID
    questions: list[QuizQuestionOut]


class QuizAnswer(BaseModel):
    question_id: uuid.UUID
    selected_index: int = Field(ge=0)


class QuizSubmitRequest(BaseModel):
    reading_plan_id: uuid.UUID
    chapter_id: uuid.UUID
    answers: list[QuizAnswer]


class WrongAnswerHint(BaseModel):
    question_id: uuid.UUID
    verse_reference: str


class QuizSubmitResponse(BaseModel):
    score: int
    total_questions: int
    passed: bool
    attempt_count: int
    hints: list[WrongAnswerHint] = []  # populated only for wrong answers, so the reader can go re-read that verse


# ---------------------------------------------------------------------
# Admin quiz management
# ---------------------------------------------------------------------
class QuizQuestionAdminOut(BaseModel):
    """Includes correct_index - admin-only, never sent to a quiz-taker."""
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    chapter_id: uuid.UUID
    question: str
    options: list[str]
    correct_index: int
    verse_reference: str
    age_group: str


class QuizQuestionCreate(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    options: list[str] = Field(min_length=2, max_length=6)
    correct_index: int = Field(ge=0)
    verse_reference: str = Field(min_length=1, max_length=60)
    age_group: str = Field(default="adult", pattern="^(adult|13-17|9-12|6-8|3-5)$")


class QuizQuestionUpdate(BaseModel):
    question: Optional[str] = Field(default=None, min_length=3, max_length=1000)
    options: Optional[list[str]] = Field(default=None, min_length=2, max_length=6)
    correct_index: Optional[int] = Field(default=None, ge=0)
    verse_reference: Optional[str] = Field(default=None, min_length=1, max_length=60)
    age_group: Optional[str] = Field(default=None, pattern="^(adult|13-17|9-12|6-8|3-5)$")
