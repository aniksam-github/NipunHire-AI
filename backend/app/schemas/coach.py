from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.candidate_intelligence import CareerCoachResult


class CoachQuestion(BaseModel):
    question: str = Field(min_length=2, max_length=4_000)


class CoachMessageResponse(BaseModel):
    id: str
    question: str
    answer: str
    created_at: datetime


class CoachPlanHistoryResponse(CoachMessageResponse):
    career_plan: CareerCoachResult | None = None
    resume_id: str | None = None
