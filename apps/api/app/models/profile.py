"""
Profile Beanie Document Model — stores candidate profile details, education,
work experience, projects, skills, certifications, and social links.
"""

from datetime import datetime, timezone
from typing import Any, Optional

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class EducationItem(BaseModel):
    school: str
    degree: str
    field_of_study: str
    start_year: int
    end_year: Optional[int] = None


class ExperienceItem(BaseModel):
    company: str
    role: str
    location: str = "Remote"
    start_date: str
    end_date: Optional[str] = "Present"
    description: str = ""
    skills_used: list[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    title: str
    description: str
    tech_stack: list[str] = Field(default_factory=list)
    github_url: Optional[str] = None
    live_url: Optional[str] = None


class Profile(Document):
    """
    Candidate Profile document stored in MongoDB.
    """

    candidate_id: PydanticObjectId = Field(..., description="User ID of the candidate")
    headline: str = Field(default="Full Stack & AI Engineer", max_length=150)
    bio: str = Field(default="", max_length=1000)

    education: list[EducationItem] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)

    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    is_public: bool = Field(default=False)

    completion_percentage: int = Field(default=20, ge=0, le=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "profiles"
        indexes = [
            "candidate_id",
            "completion_percentage",
        ]
