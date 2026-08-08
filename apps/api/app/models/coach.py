"""Candidate career-coach conversation history."""

from datetime import datetime, timezone

from beanie import Document, PydanticObjectId
from pydantic import Field

from app.schemas.candidate_intelligence import CareerCoachResult


class CoachMessage(Document):
    candidate_id: PydanticObjectId
    question: str = Field(min_length=2, max_length=4_000)
    answer: str = Field(min_length=1, max_length=8_000)
    career_plan: CareerCoachResult | None = None
    resume_id: PydanticObjectId | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "coach_messages"
        indexes = ["candidate_id", [("created_at", -1)]]
