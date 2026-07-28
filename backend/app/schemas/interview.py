from datetime import datetime

from pydantic import BaseModel, Field

from app.models.interview import InterviewType


class InterviewCreate(BaseModel):
    interview_type: InterviewType
    topic: str = Field(min_length=2, max_length=100)
    company: str | None = Field(default=None, max_length=100)
    position: str | None = Field(default=None, max_length=100)
    question_count: int = Field(default=3, ge=1, le=10)


class InterviewSubmit(BaseModel):
    answers: list[str] = Field(min_length=1, max_length=10)


class InterviewResponse(BaseModel):
    id: str
    interview_type: InterviewType
    topic: str
    company: str | None
    position: str | None
    questions: list[str]
    answers: list[str]
    feedback: list[str]
    overall_score: int | None
    completed_at: datetime | None
    created_at: datetime
