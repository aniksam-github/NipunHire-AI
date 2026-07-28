"""Persistent interview-practice sessions and evaluations."""

from datetime import datetime, timezone
from enum import Enum

from beanie import Document, PydanticObjectId
from pydantic import Field


class InterviewType(str, Enum):
    TECHNICAL = "technical"
    HR = "hr"
    BEHAVIORAL = "behavioral"
    COMPANY_SPECIFIC = "company_specific"


class InterviewSession(Document):
    candidate_id: PydanticObjectId
    interview_type: InterviewType
    topic: str = Field(min_length=2, max_length=100)
    company: str | None = None
    position: str | None = None
    questions: list[str] = Field(default_factory=list)
    answers: list[str] = Field(default_factory=list)
    feedback: list[str] = Field(default_factory=list)
    overall_score: int | None = Field(default=None, ge=0, le=100)
    completed_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "interview_sessions"
        indexes = ["candidate_id", "interview_type", [("created_at", -1)]]
