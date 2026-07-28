from datetime import datetime

from pydantic import BaseModel, Field


class CoachQuestion(BaseModel):
    question: str = Field(min_length=2, max_length=4_000)


class CoachMessageResponse(BaseModel):
    id: str
    question: str
    answer: str
    created_at: datetime
