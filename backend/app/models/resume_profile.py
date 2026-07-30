"""Database record for structured intelligence extracted from one resume."""

from datetime import datetime, timezone

from beanie import Document, PydanticObjectId
from pydantic import Field

from app.schemas.resume_intelligence import (
    ResumeContact,
    ResumeEducation,
    ResumeExperience,
    ResumeProject,
)


class ResumeProfile(Document):
    """Parsed and summarized candidate data linked to an uploaded resume."""

    resume_id: PydanticObjectId
    candidate_id: PydanticObjectId
    full_name: str | None = None
    contact: ResumeContact = Field(default_factory=ResumeContact)
    education: list[ResumeEducation] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[ResumeProject] = Field(default_factory=list)
    experience: list[ResumeExperience] = Field(default_factory=list)
    professional_summary: str | None = None
    key_highlights: list[str] = Field(default_factory=list)
    career_snapshot: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "resume_profiles"
        indexes = ["resume_id", "candidate_id"]
