"""
Pydantic schemas for Job Application pipeline tracking.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.application import ApplicationStatus, TimelineEvent


class ApplicationCreate(BaseModel):
    job_id: str = Field(..., description="Job ObjectId string")
    resume_id: Optional[str] = None
    notes: Optional[str] = None


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
    note: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: str
    candidate_id: str
    job_id: str
    resume_id: Optional[str] = None
    status: ApplicationStatus
    notes: Optional[str] = None
    timeline: list[TimelineEvent]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
