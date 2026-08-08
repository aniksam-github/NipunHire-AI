"""Typed contracts for Phase 3 structured resume screening."""

from pydantic import BaseModel, Field


class ResumeAnalysisResult(BaseModel):
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    ats_compatibility_score: int = Field(ge=0, le=100)
    improvement_suggestions: list[str] = Field(default_factory=list)
    confidence_score: int = Field(ge=0, le=100)


class CategorizedSkillsResult(BaseModel):
    technical_skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)


class ResumeImprovementResult(BaseModel):
    recommended_projects: list[str] = Field(default_factory=list)
    skills_to_learn: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)


class ResumeScreeningResponse(BaseModel):
    profile_id: str
    analysis: ResumeAnalysisResult
    skills: CategorizedSkillsResult
    improvements: ResumeImprovementResult
