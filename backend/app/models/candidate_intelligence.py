"""Persisted review-only outputs for Phase 5 candidate intelligence."""

from datetime import datetime, timezone

from beanie import Document, PydanticObjectId
from pydantic import Field

from app.schemas.candidate_intelligence import ATSOptimizerResult, ResumeOptimizerResult


class ResumeOptimizationSuggestion(Document):
    candidate_id: PydanticObjectId
    resume_id: PydanticObjectId
    result: ResumeOptimizerResult
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "resume_optimization_suggestions"
        indexes = ["candidate_id", "resume_id", [("created_at", -1)]]


class ATSOptimizationSuggestion(Document):
    candidate_id: PydanticObjectId
    resume_id: PydanticObjectId
    job_id: PydanticObjectId
    result: ATSOptimizerResult
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "ats_optimization_suggestions"
        indexes = ["candidate_id", "resume_id", "job_id", [("created_at", -1)]]
