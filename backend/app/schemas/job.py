"""
Pydantic schemas for the Jobs module — HTTP request/response transfer objects.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.job import EmploymentType


class JobCreate(BaseModel):
    """Payload to create a new job posting."""

    title: str = Field(..., min_length=3, max_length=150, examples=["Senior Full Stack Engineer"])
    description: str = Field(..., min_length=10, examples=["We are looking for a Senior Full Stack Engineer..."])
    department: str = Field(default="Engineering", max_length=100, examples=["Engineering"])
    location: str = Field(default="Remote", max_length=100, examples=["Bengaluru, India / Remote"])
    employment_type: EmploymentType = Field(default=EmploymentType.FULL_TIME)
    min_experience_years: int = Field(default=2, ge=0)
    required_skills: list[str] = Field(default_factory=list, examples=[["FastAPI", "React", "TypeScript", "MongoDB"]])
    optional_skills: list[str] = Field(default_factory=list, examples=[["Docker", "Tailwind CSS"]])


class JobUpdate(BaseModel):
    """Payload to partially update a job posting."""

    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    min_experience_years: Optional[int] = None
    required_skills: Optional[list[str]] = None
    optional_skills: Optional[list[str]] = None
    is_active: Optional[bool] = None


class JobResponse(BaseModel):
    """Safe public representation of a Job posting."""

    id: str = Field(..., description="MongoDB ObjectId as hex string")
    title: str
    description: str
    department: str
    location: str
    employment_type: EmploymentType
    min_experience_years: int
    required_skills: list[str]
    optional_skills: list[str]
    is_active: bool
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
