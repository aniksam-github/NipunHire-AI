"""
Application Beanie Document Model — tracks candidate job application status pipeline.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class ApplicationStatus(str, Enum):
    SAVED = "saved"
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    OFFER_RECEIVED = "offer_received"
    REJECTED = "rejected"


class TimelineEvent(BaseModel):
    status: ApplicationStatus
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    note: Optional[str] = None


class Application(Document):
    """
    Candidate Job Application pipeline record stored in MongoDB.
    """

    candidate_id: PydanticObjectId = Field(...)
    job_id: PydanticObjectId = Field(...)
    resume_id: Optional[PydanticObjectId] = None

    status: ApplicationStatus = Field(default=ApplicationStatus.APPLIED)
    notes: Optional[str] = None
    timeline: list[TimelineEvent] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "applications"
        indexes = [
            "candidate_id",
            "job_id",
            "status",
            [("updated_at", -1)],
        ]
