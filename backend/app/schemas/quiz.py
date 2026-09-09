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
