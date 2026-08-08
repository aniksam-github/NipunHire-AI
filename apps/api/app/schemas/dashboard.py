"""Response contracts for the candidate career dashboard."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.application import ApplicationStatus


class ApplicationStatusSummary(BaseModel):
    saved: int = 0
    applied: int = 0
    shortlisted: int = 0
    interview_scheduled: int = 0
    offer_received: int = 0
    rejected: int = 0


class RecentApplication(BaseModel):
    id: str
    job_id: str
    status: ApplicationStatus
    updated_at: datetime


class CandidateDashboardResponse(BaseModel):
    profile_completion_percentage: int = Field(ge=0, le=100)
    resume_health_score: int | None = Field(default=None, ge=0, le=100)
    application_summary: ApplicationStatusSummary
    upcoming_interviews: int = Field(default=0, ge=0)
    recent_applications: list[RecentApplication] = Field(default_factory=list)
    daily_recommendations: list[str] = Field(default_factory=list)
    skill_improvement_suggestions: list[str] = Field(default_factory=list)
    weekly_progress: dict[str, int] = Field(default_factory=dict)
