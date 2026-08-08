"""Pydantic schemas for Phase 9 Research Features (Explainable AI, Bias Process Auditing, Resume Anomaly Detection, Interview Cheat Risk)."""

from typing import Any
from pydantic import BaseModel, Field


# --- Module 1: Unified Explanation Trace & Consistency Metrics ---
class ConsistencyMetrics(BaseModel):
    alignment_score: float = Field(..., ge=0.0, le=100.0, description="Alignment score between recommendation and factor evidence")
    is_consistent: bool = Field(..., description="True if no major logical contradictions exist across phase scores")
    flagged_mismatches: list[str] = Field(default_factory=list, description="List of logical score/factor mismatches")


class ExplanationTraceResponse(BaseModel):
    """
    Academic Research Methodology:
    Consolidates multi-phase explainability outputs (Phase 4 match factors, Phase 6 interview dimensions,
    Phase 7 coding complexity) into a unified decision trace for auditing.
    """

    candidate_id: str
    job_id: str
    match_trace: dict[str, Any] | None = None
    interview_trace: dict[str, Any] | None = None
    coding_trace: dict[str, Any] | None = None
    consistency_metrics: ConsistencyMetrics
    human_review_disclaimer: str = Field(
        default="DISCLAIMER: Explanation traces and consistency metrics are analytical decision-support tools for human review. They do not constitute automated employment decisions."
    )


# --- Module 2: Bias Detection (Process Auditing) ---
class ScoreStatistics(BaseModel):
    mean: float = Field(..., ge=0.0, le=100.0)
    median: float = Field(..., ge=0.0, le=100.0)
    std_dev: float = Field(..., ge=0.0)
    min_score: float = Field(..., ge=0.0, le=100.0)
    max_score: float = Field(..., ge=0.0, le=100.0)


class ProcessPatternFlag(BaseModel):
    pattern_name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    severity: str = Field(..., description="info | warning | critical")
    statistic_summary: str = Field(..., min_length=1)


class ProcessBiasAuditResponse(BaseModel):
    """
    Academic Research Methodology:
    Process-Level Audit vs Demographic Profiling. Evaluates statistical score distribution and variance
    across a job candidate pool to audit evaluation consistency. Contains ZERO protected demographic data.
    """

    job_id: str
    total_applicants_audited: int = Field(..., ge=0)
    score_statistics: ScoreStatistics
    flagged_process_patterns: list[ProcessPatternFlag] = Field(default_factory=list)
    dominant_rejection_factors: list[dict[str, Any]] = Field(default_factory=list)
    human_review_disclaimer: str = Field(
        default="DISCLAIMER: This statistical process audit evaluates scoring variance across a job applicant pool. It contains zero demographic data and is an advisory signal for human recruiter review, not a bias determination."
    )


# --- Module 3: Resume Fraud / Anomaly Detection ---
class ResumeInconsistencyFlag(BaseModel):
    issue_type: str = Field(..., min_length=1, description="overlapping_employment | unsupported_skill | timeline_gap | education_mismatch")
    description: str = Field(..., min_length=1)
    confidence_level: str = Field(..., description="low | medium | high")
    supporting_evidence: str | None = Field(default=None)


class ResumeAnomalyCheckResponse(BaseModel):
    """
    Academic Research Methodology:
    Heuristic & NLP internal consistency audit of stated resume content.
    Provides decision-support risk signals for human recruiter review without external verification claims.
    """

    resume_id: str
    candidate_id: str
    overall_risk_score: int = Field(..., ge=0, le=100)
    flagged_inconsistencies: list[ResumeInconsistencyFlag] = Field(default_factory=list)
    requires_human_review: bool = Field(default=True)
    human_review_disclaimer: str = Field(
        default="DISCLAIMER: This internal consistency audit evaluates stated resume text for timeline and claim contradictions. It is a decision-support signal for human recruiter review and does not constitute a determination of fraud."
    )


# --- Module 4: Interview Cheat Risk Detection ---
class InterviewAnomalyFlag(BaseModel):
    anomaly_type: str = Field(..., min_length=1, description="phrasing_shift | unnatural_polish | boilerplate_repetition")
    turn_index: int = Field(..., ge=0)
    description: str = Field(..., min_length=1)
    confidence_level: str = Field(..., description="low | medium | high")


class InterviewCheatRiskResponse(BaseModel):
    """
    Academic Research Methodology:
    Stylometric anomaly detection in multi-turn interactive Q&A history.
    Informational decision-support signal for human review; never auto-triggers candidate rejection.
    """

    session_id: str
    candidate_id: str
    cheat_risk_score: int = Field(..., ge=0, le=100)
    risk_level: str = Field(..., description="low | moderate | high")
    flagged_anomalies: list[InterviewAnomalyFlag] = Field(default_factory=list)
    supporting_reasoning: str = Field(..., min_length=1)
    is_informational_only: bool = Field(default=True)
    human_review_disclaimer: str = Field(
        default="DISCLAIMER: This stylometric analysis is an informational decision-support signal for human review. It must never serve as the sole basis for candidate rejection."
    )
