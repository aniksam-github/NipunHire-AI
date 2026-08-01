"""Pydantic schemas for Phase 6 Interview AI simulation, evaluation, and reporting."""

from datetime import datetime
from pydantic import BaseModel, Field

from app.models.interview import (
    DifficultyDecision,
    DifficultyLevel,
    HiringRecommendation,
    InterviewType,
    QuestionCategory,
    SessionStatus,
)


# --- Module 1 Schema ---
class InterviewQuestion(BaseModel):
    question_text: str = Field(..., min_length=5, description="The text of the interview question")
    category: QuestionCategory = Field(default=QuestionCategory.TECHNICAL)
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM)


class GeneratedQuestionList(BaseModel):
    questions: list[InterviewQuestion] = Field(..., min_length=1)


# --- Module 3 Schema ---
class DimensionScore(BaseModel):
    score: int = Field(..., ge=0, le=10, description="Dimension score out of 10")
    justification: str = Field(..., min_length=1, description="Justification for the dimension score")


class AnswerEvaluation(BaseModel):
    technical_correctness: DimensionScore
    communication_clarity: DimensionScore
    confidence: DimensionScore
    grammar: DimensionScore
    completeness: DimensionScore
    overall_turn_score: int = Field(..., ge=0, le=100, description="Overall turn score out of 100")
    overall_feedback: str = Field(..., min_length=1, description="Constructive feedback for the turn")


# --- Module 4 Schema ---
class IdealAnswerComparison(BaseModel):
    ideal_answer: str = Field(..., min_length=5, description="Model ideal answer benchmark")
    key_strengths: list[str] = Field(default_factory=list, description="Strengths demonstrated by candidate")
    missing_points: list[str] = Field(default_factory=list, description="Key points or nuances missed by candidate")
    comparison_summary: str = Field(..., min_length=1, description="Summary comparison against ideal answer")


# --- Module 2 Adaptive Schemas ---
class DifficultyAdjustment(BaseModel):
    difficulty_decision: DifficultyDecision
    reasoning: str = Field(..., min_length=1)
    next_difficulty: DifficultyLevel


class AdaptiveNextQuestionResponse(BaseModel):
    difficulty_decision: DifficultyDecision
    reasoning: str = Field(..., min_length=1)
    next_difficulty: DifficultyLevel
    next_question: InterviewQuestion


class InterviewTurn(BaseModel):
    turn_index: int = Field(..., ge=0)
    question: InterviewQuestion
    candidate_answer: str
    evaluation: AnswerEvaluation
    ideal_comparison: IdealAnswerComparison
    difficulty_adjustment: DifficultyAdjustment | None = None


# --- Module 5 Schema ---
class InterviewReport(BaseModel):
    overall_score: int = Field(..., ge=0, le=100, description="Aggregated overall score out of 100")
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    hiring_recommendation: HiringRecommendation
    summary_justification: str = Field(..., min_length=1)
    category_breakdown: dict[str, float] = Field(default_factory=dict)


# --- API Request & Response Schemas ---
class InterviewSessionStartRequest(BaseModel):
    job_id: str = Field(..., description="Target Job ID")
    initial_difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM)
    total_questions: int = Field(default=3, ge=1, le=10)


class InterviewSessionStartResponse(BaseModel):
    session_id: str
    candidate_id: str
    job_id: str
    current_question_index: int
    current_difficulty: DifficultyLevel
    status: SessionStatus
    current_question: InterviewQuestion
    created_at: datetime


class InterviewTurnSubmitRequest(BaseModel):
    answer: str = Field(..., min_length=1, description="Candidate's submitted answer for the current question")


class InterviewTurnSubmitResponse(BaseModel):
    session_id: str
    turn_index: int
    evaluation: AnswerEvaluation
    ideal_comparison: IdealAnswerComparison
    difficulty_adjustment: DifficultyAdjustment | None = None
    next_question: InterviewQuestion | None = None
    session_completed: bool
    current_difficulty: DifficultyLevel


class InterviewReportResponse(BaseModel):
    session_id: str
    candidate_id: str
    job_id: str
    completed_at: datetime
    report: InterviewReport


class InterviewSessionResponse(BaseModel):
    id: str
    candidate_id: str
    job_id: str | None
    interview_type: InterviewType
    initial_difficulty: DifficultyLevel
    current_difficulty: DifficultyLevel
    current_question_index: int
    total_questions: int
    status: SessionStatus
    current_question: InterviewQuestion | None
    turns: list[InterviewTurn]
    final_report: InterviewReport | None
    created_at: datetime
    completed_at: datetime | None


# --- Legacy Practice Schemas (Backward Compatibility) ---
class InterviewCreate(BaseModel):
    interview_type: InterviewType = Field(default=InterviewType.TECHNICAL)
    topic: str = Field(default="General Technical", min_length=2, max_length=100)
    company: str | None = Field(default=None, max_length=100)
    position: str | None = Field(default=None, max_length=100)
    question_count: int = Field(default=3, ge=1, le=10)


class InterviewSubmit(BaseModel):
    answers: list[str] = Field(min_length=1, max_length=10)


class InterviewResponse(BaseModel):
    id: str
    interview_type: InterviewType
    topic: str
    company: str | None
    position: str | None
    questions: list[str]
    answers: list[str]
    feedback: list[str]
    overall_score: int | None
    completed_at: datetime | None
    created_at: datetime
