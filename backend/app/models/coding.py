"""Safe, persisted coding-practice submissions (no untrusted code execution)."""

from datetime import datetime, timezone
from enum import Enum

from beanie import Document, PydanticObjectId
from pydantic import Field


class CodingLanguage(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    SQL = "sql"


class CodingDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class CodingSubmission(Document):
    candidate_id: PydanticObjectId
    language: CodingLanguage
    difficulty: CodingDifficulty
    question_id: str
    question_title: str
    code: str = Field(min_length=1, max_length=50_000)
    correctness_score: int = Field(ge=0, le=100)
    code_quality_score: int = Field(ge=0, le=100)
    overall_score: int = Field(ge=0, le=100)
    feedback: list[str] = Field(default_factory=list)
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "coding_submissions"
        indexes = ["candidate_id", "language", [("submitted_at", -1)]]
