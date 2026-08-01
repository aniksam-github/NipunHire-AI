"""Pydantic schemas for Phase 7 Coding AI question generation, submission, review, and consolidated feedback."""

from datetime import datetime
from pydantic import BaseModel, Field

from app.models.coding import CodingDifficulty, CodingLanguage


class CodingExample(BaseModel):
    input: str = Field(..., description="Sample input parameter format")
    output: str = Field(..., description="Expected sample output format")
    explanation: str | None = Field(default=None, description="Detailed explanation of example execution")


# --- Step 1 Question Schemas ---
class CodingQuestion(BaseModel):
    id: str
    title: str = Field(..., min_length=2, max_length=150)
    problem_statement: str = Field(..., min_length=10)
    input_output_format: str = Field(default="")
    examples: list[CodingExample] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    difficulty: CodingDifficulty = Field(default=CodingDifficulty.MEDIUM)
    topics: list[str] = Field(default_factory=list)
    starter_code: str | None = Field(default=None)


class CodingQuestionGenerated(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    problem_statement: str = Field(..., min_length=10)
    input_output_format: str = Field(default="")
    examples: list[CodingExample] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    difficulty: CodingDifficulty = Field(default=CodingDifficulty.MEDIUM)
    topics: list[str] = Field(default_factory=list)
    starter_code: str | None = Field(default=None)


class CodingQuestionGenerateRequest(BaseModel):
    job_id: str = Field(..., description="Target Job ID")
    difficulty: CodingDifficulty = Field(default=CodingDifficulty.MEDIUM)


class CodingQuestionGenerateResponse(BaseModel):
    question: CodingQuestion
    job_id: str
    candidate_id: str
    created_at: datetime


# --- Step 2 & 3 Submission & Review Schemas ---
class CodingSubmissionCreate(BaseModel):
    question_id: str = Field(..., description="ID of the generated coding question")
    language: CodingLanguage = Field(default=CodingLanguage.PYTHON)
    code: str = Field(..., min_length=1, max_length=50_000, description="Submitted plain-text source code")


class CodingReviewResult(BaseModel):
    correctness_score: int = Field(..., ge=0, le=100, description="Logical correctness score out of 100")
    code_quality_score: int = Field(..., ge=0, le=100, description="Code quality and style score out of 100")
    overall_score: int = Field(..., ge=0, le=100, description="Overall weighted score out of 100")
    correctness_assessment: str = Field(..., min_length=1, description="Assessment of logical correctness")
    is_incomplete_or_invalid: bool = Field(default=False, description="True if code has syntax errors or is incomplete")
    identified_bugs: list[str] = Field(default_factory=list, description="Bugs, syntax errors, or missed edge cases")
    time_complexity: str = Field(..., min_length=1, description="Stated time complexity (e.g. O(N log N))")
    space_complexity: str = Field(..., min_length=1, description="Stated space complexity (e.g. O(N))")
    complexity_explanation: str = Field(..., min_length=1, description="Explanation of complexity analysis")
    code_quality_observations: list[str] = Field(default_factory=list)
    optimization_suggestions: list[str] = Field(default_factory=list)


# --- Step 4 Consolidated Feedback Schema ---
class ConsolidatedCodingFeedbackResponse(BaseModel):
    submission_id: str
    candidate_id: str
    job_id: str | None = None
    question: CodingQuestion
    language: CodingLanguage
    submitted_code: str
    submitted_at: datetime
    review: CodingReviewResult


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
