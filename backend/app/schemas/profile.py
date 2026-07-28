"""
Pydantic schemas for Candidate Profile management.
"""

from typing import Optional
from pydantic import BaseModel, Field
from app.models.profile import EducationItem, ExperienceItem, ProjectItem


class ProfileUpdate(BaseModel):
    headline: Optional[str] = None
    bio: Optional[str] = None
    education: Optional[list[EducationItem]] = None
    experience: Optional[list[ExperienceItem]] = None
    projects: Optional[list[ProjectItem]] = None
    skills: Optional[list[str]] = None
    certifications: Optional[list[str]] = None
    languages: Optional[list[str]] = None
    achievements: Optional[list[str]] = None
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    is_public: Optional[bool] = None


class ProfileResponse(BaseModel):
    id: str
    candidate_id: str
    headline: str
    bio: str
    education: list[EducationItem]
    experience: list[ExperienceItem]
    projects: list[ProjectItem]
    skills: list[str]
    certifications: list[str]
    languages: list[str]
    achievements: list[str]
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    is_public: bool
    completion_percentage: int

    class Config:
        from_attributes = True
