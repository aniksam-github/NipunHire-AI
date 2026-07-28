"""
Pydantic schemas for Job Matching & JD Comparison.
"""

from typing import Optional
from pydantic import BaseModel, Field


class MatchRequest(BaseModel):
    job_id: str = Field(..., description="Job position ObjectId string")
    resume_id: Optional[str] = Field(None, description="Optional specific resume ObjectId string")


class MatchResponse(BaseModel):
    id: str
    candidate_id: str
    job_id: str
    resume_id: Optional[str] = None
    match_score: float
    matched_skills: list[str]
    missing_required_skills: list[str]
    missing_optional_skills: list[str]
    strengths: list[str]
    weaknesses: list[str]
    application_readiness_score: int
    recommendations: list[str]

    class Config:
        from_attributes = True
