"""Structured AI contracts used by the resume intelligence pipeline."""

from pydantic import BaseModel, Field


class ResumeContact(BaseModel):
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None


class ResumeEducation(BaseModel):
    institution: str
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class ResumeExperience(BaseModel):
    company: str
    title: str
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    highlights: list[str] = Field(default_factory=list)


class ResumeProject(BaseModel):
    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    url: str | None = None


class ResumeParsingResult(BaseModel):
    full_name: str | None = None
    contact: ResumeContact = Field(default_factory=ResumeContact)
    education: list[ResumeEducation] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[ResumeProject] = Field(default_factory=list)
    experience: list[ResumeExperience] = Field(default_factory=list)


class ResumeSummaryResult(BaseModel):
    professional_summary: str
    key_highlights: list[str] = Field(default_factory=list)
    career_snapshot: str
