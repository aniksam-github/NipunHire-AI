"""Pydantic schemas for Phase 8 Recruiter AI aggregation and decision-support features."""

from pydantic import BaseModel, Field, model_validator

from app.schemas.interview import InterviewReport
from app.schemas.resume_matching import RecruiterRecommendation


# --- Module 1: Candidate Summary ---
class CandidateSummaryReport(BaseModel):
    candidate_id: str
    key_highlights: list[str] = Field(default_factory=list)
    overall_assessment: str = Field(..., min_length=1)
    standout_signals: dict[str, list[str]] = Field(default_factory=dict)
    available_data_sources: list[str] = Field(default_factory=list)


# --- Module 2: Candidate Comparison ---
class CandidateComparisonRequest(BaseModel):
    job_id: str = Field(..., description="Target Job ID for comparison context")
    candidate_ids: list[str] = Field(..., min_length=2, description="List of candidate IDs to compare side-by-side")


class CandidateComparisonEntry(BaseModel):
    candidate_id: str
    full_name: str | None = None
    relative_strengths: list[str] = Field(default_factory=list)
    dimension_ratings: dict[str, float] = Field(default_factory=dict)


class CandidateComparisonResult(BaseModel):
    job_id: str
    candidates_compared: list[str]
    per_candidate_breakdown: list[CandidateComparisonEntry]
    dimension_leaders: dict[str, str] = Field(default_factory=dict)
    comparison_summary: str = Field(..., min_length=1)


# --- Module 3: Candidate Ranking ---
class RankingWeights(BaseModel):
    match_weight: float = Field(default=0.4, ge=0.0, le=1.0)
    interview_weight: float = Field(default=0.35, ge=0.0, le=1.0)
    coding_weight: float = Field(default=0.25, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_weights_sum(self):
        total = round(self.match_weight + self.interview_weight + self.coding_weight, 4)
        if total <= 0:
            raise ValueError("Ranking weights sum must be greater than zero")
        return self


class CandidateRankingRequest(BaseModel):
    candidate_ids: list[str] | None = Field(default=None, description="Optional filter of candidate IDs to rank")
    weights: RankingWeights = Field(default_factory=RankingWeights)


class RankedCandidateEntry(BaseModel):
    rank: int = Field(..., ge=1, description="Rank position (1-indexed)")
    candidate_id: str
    composite_score: float = Field(..., ge=0.0, le=100.0)
    sub_scores: dict[str, float | None] = Field(default_factory=dict)
    justification: str = Field(..., min_length=1)


class CandidateRankingList(BaseModel):
    job_id: str
    weights_used: RankingWeights
    rankings: list[RankedCandidateEntry]


# --- Module 4: Interview Summary (Recruiter View) ---
class RecruiterInterviewHighlight(BaseModel):
    turn_index: int
    question_text: str
    category: str
    candidate_answer_summary: str
    turn_score: int


class RecruiterInterviewSummaryResponse(BaseModel):
    session_id: str
    candidate_id: str
    job_id: str | None = None
    overall_score: int | None = None
    hiring_recommendation: str | None = None
    status: str
    key_qa_highlights: list[RecruiterInterviewHighlight] = Field(default_factory=list)
    final_report: InterviewReport | None = None


# --- Module 5: Aggregate Hiring Recommendation ---
class AggregateHiringRecommendationRequest(BaseModel):
    candidate_id: str
    job_id: str | None = Field(default=None, description="Optional Job ID context")


class AggregateHiringRecommendationResponse(BaseModel):
    candidate_id: str
    job_id: str | None = None
    recommendation: RecruiterRecommendation
    confidence_score: int = Field(..., ge=0, le=100)
    grounded_reason: str = Field(..., min_length=1)
    key_factors: list[str] = Field(default_factory=list)


# --- Module 6: Job Description Generator ---
class JobDescriptionGenerateRequest(BaseModel):
    role_title: str = Field(..., min_length=2, max_length=150)
    required_skills: list[str] = Field(..., min_length=1)
    seniority_level: str = Field(default="Senior", max_length=50)


class GeneratedJobDescription(BaseModel):
    role_title: str
    seniority_level: str
    summary: str = Field(..., min_length=10)
    responsibilities: list[str] = Field(default_factory=list)
    required_qualifications: list[str] = Field(default_factory=list)
    preferred_qualifications: list[str] = Field(default_factory=list)
