"""Persistent AI-driven adaptive interview sessions and evaluations."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class DifficultyDecision(str, Enum):
    INCREASE = "increase"
    DECREASE = "decrease"
    MAINTAIN = "maintain"


class QuestionCategory(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SITUATIONAL = "situational"


class HiringRecommendation(str, Enum):
    STRONG_HIRE = "strong_hire"
    HIRE = "hire"
    LEAN_HIRE = "lean_hire"
    LEAN_REJECT = "lean_reject"
    REJECT = "reject"


class SessionStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    READY_TO_COMPLETE = "ready_to_complete"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class InterviewType(str, Enum):
    TECHNICAL = "technical"
    HR = "hr"
    BEHAVIORAL = "behavioral"
    COMPANY_SPECIFIC = "company_specific"


class InterviewQuestionModel(BaseModel):
    question_text: str
    category: QuestionCategory = Field(default=QuestionCategory.TECHNICAL)
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM)


class DimensionScoreModel(BaseModel):
    score: int = Field(ge=0, le=10)
    justification: str


class AnswerEvaluationModel(BaseModel):
    technical_correctness: DimensionScoreModel
    communication_clarity: DimensionScoreModel
    confidence: DimensionScoreModel
    grammar: DimensionScoreModel
    completeness: DimensionScoreModel
    overall_turn_score: int = Field(ge=0, le=100)
    overall_feedback: str


class IdealAnswerComparisonModel(BaseModel):
    ideal_answer: str
    key_strengths: list[str] = Field(default_factory=list)
    missing_points: list[str] = Field(default_factory=list)
    comparison_summary: str


class DifficultyAdjustmentModel(BaseModel):
    difficulty_decision: DifficultyDecision
    reasoning: str
    next_difficulty: DifficultyLevel


class InterviewTurnModel(BaseModel):
    turn_index: int
    question: InterviewQuestionModel
    candidate_answer: str
    evaluation: AnswerEvaluationModel
    ideal_comparison: IdealAnswerComparisonModel
    difficulty_adjustment: DifficultyAdjustmentModel | None = None


class InterviewReportModel(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    hiring_recommendation: HiringRecommendation
    summary_justification: str
    category_breakdown: dict[str, float] = Field(default_factory=dict)


class InterviewSession(Document):
    """
    Stateful Interview Session document stored in MongoDB.
    Enables turn-by-turn resumption across separate API requests.
    """

    candidate_id: PydanticObjectId
    job_id: PydanticObjectId | None = None
    interview_type: InterviewType = Field(default=InterviewType.TECHNICAL)
    topic: str = Field(default="General Technical & Behavioral", min_length=2, max_length=100)
    company: str | None = None
    position: str | None = None

    # Phase 6 Adaptive Session State
    initial_difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM)
    current_difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM)
    current_question_index: int = Field(default=0, ge=0)
    total_questions: int = Field(default=3, ge=1, le=10)
    status: SessionStatus = Field(default=SessionStatus.IN_PROGRESS)

    question_pool: list[InterviewQuestionModel] = Field(default_factory=list)
    turns: list[InterviewTurnModel] = Field(default_factory=list)
    final_report: InterviewReportModel | None = None

    # Legacy fields for backward compatibility
    questions: list[str] = Field(default_factory=list)
    answers: list[str] = Field(default_factory=list)
    feedback: list[str] = Field(default_factory=list)
    overall_score: int | None = Field(default=None, ge=0, le=100)

    completed_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "interview_sessions"
        indexes = [
            "candidate_id",
            "job_id",
            "status",
            "interview_type",
            [("created_at", -1)],
        ]
