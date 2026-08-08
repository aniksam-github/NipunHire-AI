"""Persistent research feature records: resume anomaly reports and interview cheat risk reports."""

from datetime import datetime, timezone

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class ResumeInconsistencyItem(BaseModel):
    issue_type: str
    description: str
    confidence_level: str
    supporting_evidence: str | None = None


class ResumeAnomalyReport(Document):
    """
    Recruiter-facing internal consistency audit for resume text.
    Visible ONLY to recruiters, never shown to candidates.
    """

    resume_id: PydanticObjectId
    candidate_id: PydanticObjectId
    overall_risk_score: int = Field(ge=0, le=100)
    flagged_inconsistencies: list[ResumeInconsistencyItem] = Field(default_factory=list)
    requires_human_review: bool = Field(default=True)
    human_review_disclaimer: str = Field(
        default="DISCLAIMER: This internal consistency audit is a decision-support signal for human recruiter review. It does not constitute a determination of fraud."
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "resume_anomaly_reports"
        indexes = ["resume_id", "candidate_id", [("created_at", -1)]]


class InterviewAnomalyItem(BaseModel):
    anomaly_type: str
    turn_index: int
    description: str
    confidence_level: str


class InterviewCheatRiskReport(Document):
    """
    Recruiter-facing stylometric anomaly report for interview Q&A history.
    Informational decision-support signal for human review.
    """

    session_id: PydanticObjectId
    candidate_id: PydanticObjectId
    cheat_risk_score: int = Field(ge=0, le=100)
    risk_level: str = Field(default="low")
    flagged_anomalies: list[InterviewAnomalyItem] = Field(default_factory=list)
    supporting_reasoning: str
    is_informational_only: bool = Field(default=True)
    human_review_disclaimer: str = Field(
        default="DISCLAIMER: This stylometric analysis is an informational decision-support signal for human review. It must never serve as the sole basis for candidate rejection."
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "interview_cheat_risk_reports"
        indexes = ["session_id", "candidate_id", [("created_at", -1)]]
