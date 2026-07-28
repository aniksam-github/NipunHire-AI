from datetime import datetime

from pydantic import BaseModel, Field

from app.models.coding import CodingDifficulty, CodingLanguage


class CodingQuestion(BaseModel):
    id: str
    title: str
    prompt: str
    language: CodingLanguage
    difficulty: CodingDifficulty
    starter_code: str


class CodingSubmissionCreate(BaseModel):
    question_id: str
    language: CodingLanguage
    code: str = Field(min_length=1, max_length=50_000)


class CodingSubmissionResponse(BaseModel):
    id: str
    language: CodingLanguage
    difficulty: CodingDifficulty
    question_id: str
    question_title: str
    correctness_score: int
    code_quality_score: int
    overall_score: int
    feedback: list[str]
    submitted_at: datetime
