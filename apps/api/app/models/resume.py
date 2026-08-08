"""
Resume Beanie Document Model — stores candidate resume metadata, extracted text,
parsed skills, ATS score, and AI quality feedback.
"""

from datetime import datetime, timezone
from typing import Any, Optional

from beanie import Document, PydanticObjectId
from pydantic import Field


class Resume(Document):
    """
    Resume document stored in MongoDB.
    """

    candidate_id: PydanticObjectId = Field(..., description="User ID of the candidate/uploader")
    filename: str = Field(..., max_length=255)
    file_path: str = Field(..., max_length=500)
    file_size_bytes: int = Field(default=0)
    page_count: int = Field(default=1)

    raw_text: str = Field(default="")
    processing_status: str = Field(default="uploaded")
    processing_error: str | None = None
    profile_id: PydanticObjectId | None = None

    # Parsed structured attributes
    parsed_name: Optional[str] = None
    parsed_email: Optional[str] = None
    parsed_phone: Optional[str] = None
    extracted_skills: list[str] = Field(default_factory=list)

    # ATS & AI Health Metrics
    ats_score: int = Field(default=0, ge=0, le=100)
    quality_breakdown: dict[str, int] = Field(
        default_factory=lambda: {
            "formatting_score": 85,
            "keyword_density_score": 80,
            "completeness_score": 90,
        }
    )
    ai_feedback: dict[str, Any] = Field(
        default_factory=lambda: {
            "missing_elements": [],
            "action_verb_suggestions": [],
            "formatting_tips": [],
        }
    )

    is_primary: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "resumes"
        indexes = [
            "candidate_id",
            "ats_score",
            "is_primary",
            [("created_at", -1)],
        ]
