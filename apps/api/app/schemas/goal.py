from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.goal import GoalCategory, GoalStatus


class GoalCreate(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    category: GoalCategory
    target_value: int = Field(default=1, ge=1)
    unit: str = Field(default="sessions", max_length=40)
    due_date: date | None = None


class GoalProgressUpdate(BaseModel):
    current_value: int = Field(ge=0)
    status: GoalStatus | None = None


class GoalResponse(BaseModel):
    id: str
    title: str
    category: GoalCategory
    target_value: int
    current_value: int
    unit: str
    due_date: date | None
    status: GoalStatus
    created_at: datetime
    updated_at: datetime


class CareerProgressResponse(BaseModel):
    active_goals: int
    completed_goals: int
    completed_interviews: int
    interview_average_score: float | None
    achievements: list[str]
