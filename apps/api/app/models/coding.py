"""Persistent AI-driven coding challenges, code submissions, and static reviews."""

from datetime import datetime, timezone
from enum import Enum

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class CodingLanguage(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    SQL = "sql"
    GO = "go"


class CodingDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class CodingExampleModel(BaseModel):
    input: str
    output: str
    explanation: str | None = None


class CodingChallenge(Document):
    """
    AI-generated coding challenge document linked to candidate and job.
    """

    candidate_id: PydanticObjectId
    job_id: PydanticObjectId | None = None
    title: str = Field(..., min_length=2, max_length=150)
    problem_statement: str = Field(..., min_length=10)
    input_output_format: str = Field(default="")
    examples: list[CodingExampleModel] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    difficulty: CodingDifficulty = Field(default=CodingDifficulty.MEDIUM)
    topics: list[str] = Field(default_factory=list)
    starter_code: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "coding_challenges"
        indexes = [
            "candidate_id",
            "job_id",
            "difficulty",
            [("created_at", -1)],
        ]


class CodingReviewModel(BaseModel):
    correctness_score: int = Field(ge=0, le=100)
    code_quality_score: int = Field(ge=0, le=100)
    overall_score: int = Field(ge=0, le=100)
    correctness_assessment: str
    is_incomplete_or_invalid: bool = Field(default=False)
    identified_bugs: list[str] = Field(default_factory=list)
    time_complexity: str = Field(default="N/A")
    space_complexity: str = Field(default="N/A")
    complexity_explanation: str = Field(default="")
    code_quality_observations: list[str] = Field(default_factory=list)
    optimization_suggestions: list[str] = Field(default_factory=list)


class CodingSubmission(Document):
    """
    Persisted candidate code submission and static AI review.
    Code is evaluated statically via AI and never executed locally.
    """

    candidate_id: PydanticObjectId
    job_id: PydanticObjectId | None = None
    question_id: str
    challenge_id: PydanticObjectId | None = None
    question_title: str
    language: CodingLanguage
    difficulty: CodingDifficulty = Field(default=CodingDifficulty.MEDIUM)
    code: str = Field(min_length=1, max_length=50_000)

    # Static AI Review
    review: CodingReviewModel | None = None

    # Scores and Feedback for backwards compatibility
    correctness_score: int = Field(default=0, ge=0, le=100)
    code_quality_score: int = Field(default=0, ge=0, le=100)
    overall_score: int = Field(default=0, ge=0, le=100)
    feedback: list[str] = Field(default_factory=list)

    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "coding_submissions"
        indexes = [
            "candidate_id",
            "job_id",
            "question_id",
            "language",
            [("submitted_at", -1)],
        ]
