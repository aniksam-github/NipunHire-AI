"""
Job Beanie Document Model — represents job postings in MongoDB.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"


class Job(Document):
    """
    Job document stored in MongoDB.
    """

    title: str = Field(..., min_length=3, max_length=150)
    description: str = Field(..., min_length=10)
    department: str = Field(default="Engineering", max_length=100)
    location: str = Field(default="Remote", max_length=100)
    employment_type: EmploymentType = Field(default=EmploymentType.FULL_TIME)
    min_experience_years: int = Field(default=0, ge=0)
    required_skills: list[str] = Field(default_factory=list)
    optional_skills: list[str] = Field(default_factory=list)
    is_active: bool = Field(default=True)
    created_by: PydanticObjectId = Field(..., description="Recruiter user ID")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "jobs"
        indexes = [
            "title",
            "department",
            "is_active",
            "created_by",
            [("created_at", -1)],
        ]
