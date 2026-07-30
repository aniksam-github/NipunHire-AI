"""Persisted Phase 3 evaluation linked to one structured resume profile."""

from datetime import datetime, timezone

from beanie import Document, PydanticObjectId
from pydantic import Field

from app.schemas.resume_screening import (
    CategorizedSkillsResult,
    ResumeAnalysisResult,
    ResumeImprovementResult,
)


class ResumeScreening(Document):
    """Analysis, skills, and improvements produced from a candidate profile."""

    profile_id: PydanticObjectId
    resume_id: PydanticObjectId
    candidate_id: PydanticObjectId
    analysis: ResumeAnalysisResult
    skills: CategorizedSkillsResult
    improvements: ResumeImprovementResult
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "resume_screenings"
        indexes = ["profile_id", "resume_id", "candidate_id"]
