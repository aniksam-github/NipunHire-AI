"""
JobMatch Beanie Document Model — stores candidate resume vs job description
semantic match scores, skill gaps, and application readiness evaluations.
"""

from datetime import datetime, timezone
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field

from app.schemas.resume_matching import BaseMatchResult, MatchRecommendation


class JobMatch(Document):
    """
    Job Match evaluation document stored in MongoDB.
    """

    candidate_id: PydanticObjectId = Field(...)
    job_id: PydanticObjectId = Field(...)
    resume_id: Optional[PydanticObjectId] = None
    profile_id: Optional[PydanticObjectId] = None

    match_score: float = Field(default=0.0, ge=0.0, le=100.0)
    matched_skills: list[str] = Field(default_factory=list)
    missing_required_skills: list[str] = Field(default_factory=list)
    missing_optional_skills: list[str] = Field(default_factory=list)

    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    application_readiness_score: int = Field(default=50, ge=0, le=100)
    recommendations: list[str] = Field(default_factory=list)
    explainable_result: BaseMatchResult | None = None
    recruiter_recommendation: MatchRecommendation | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "job_matches"
        indexes = [
            "candidate_id",
            "job_id",
            "match_score",
            [("created_at", -1)],
        ]
