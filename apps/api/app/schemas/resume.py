"""
Pydantic schemas for the Resume Center module — HTTP transfer objects.
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class QualityBreakdownSchema(BaseModel):
    completeness_score: int
    keyword_density_score: int
    formatting_score: int


class AIFeedbackSchema(BaseModel):
    missing_elements: list[str]
    action_verb_suggestions: list[str]
    formatting_tips: list[str]


class ResumeUpdateRequest(BaseModel):
    """Payload for candidate AI correction of parsed contact details and skills (Checklist #5)."""
    parsed_email: Optional[str] = None
    parsed_phone: Optional[str] = None
    extracted_skills: Optional[list[str]] = None


class ResumeResponse(BaseModel):
    """Safe public representation of a candidate's resume analysis."""

    id: str = Field(..., description="Resume ObjectId hex string")
    candidate_id: str
    filename: str
    file_size_bytes: int
    page_count: int
    parsed_name: Optional[str] = None
    parsed_email: Optional[str] = None
    parsed_phone: Optional[str] = None
    extracted_skills: list[str]
    ats_score: int
    quality_breakdown: QualityBreakdownSchema
    ai_feedback: AIFeedbackSchema
    is_primary: bool
    created_at: datetime

    class Config:
        from_attributes = True
