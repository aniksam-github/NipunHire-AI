"""Candidate goals used by the planner, streaks, and progress analytics."""

from datetime import date, datetime, timezone
from enum import Enum

from beanie import Document, PydanticObjectId
from pydantic import Field


class GoalCategory(str, Enum):
    INTERVIEW = "interview"
    SKILL = "skill"
    CODING = "coding"
    CAREER = "career"


class GoalStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"


class CareerGoal(Document):
    candidate_id: PydanticObjectId
    title: str = Field(min_length=2, max_length=160)
    category: GoalCategory
    target_value: int = Field(default=1, ge=1)
    current_value: int = Field(default=0, ge=0)
    unit: str = Field(default="sessions", max_length=40)
    due_date: date | None = None
    status: GoalStatus = GoalStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "career_goals"
        indexes = ["candidate_id", "status", [("updated_at", -1)]]
