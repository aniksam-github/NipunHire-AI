"""Typed, review-only contracts for Phase 5 candidate intelligence."""

from datetime import datetime

from pydantic import BaseModel, Field


class CareerRoadmapStep(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    rationale: str = Field(min_length=1, max_length=1_000)


class CareerCoachResult(BaseModel):
    weak_areas: list[str] = Field(default_factory=list)
    learning_roadmap: list[CareerRoadmapStep] = Field(default_factory=list)
    recommended_projects: list[str] = Field(default_factory=list)
    recommended_courses: list[str] = Field(default_factory=list)
    career_advice: str = Field(min_length=1, max_length=4_000)


class CareerCoachAnalysisRequest(BaseModel):
    resume_id: str | None = None


class CareerCoachAnalysisResponse(CareerCoachResult):
    id: str
    resume_id: str
    created_at: datetime


class ResumeTextSection(BaseModel):
    label: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1, max_length=4_000)


class ResumeRewrite(BaseModel):
    original_text: str = Field(min_length=1, max_length=4_000)
    suggested_rewrite: str = Field(min_length=1, max_length=4_000)


class ResumeOptimizerResult(BaseModel):
    rewrites: list[ResumeRewrite] = Field(min_length=1)


class ResumeOptimizerRequest(BaseModel):
    resume_id: str
    sections: list[ResumeTextSection] = Field(min_length=1, max_length=20)


class ResumeOptimizerResponse(ResumeOptimizerResult):
    id: str
    resume_id: str
    created_at: datetime


class ATSPhrasingAdjustment(BaseModel):
    original_phrase: str = Field(min_length=1, max_length=1_000)
    suggested_phrase: str = Field(min_length=1, max_length=1_000)
    rationale: str = Field(min_length=1, max_length=1_000)


class ATSOptimizerResult(BaseModel):
    missing_keywords: list[str] = Field(default_factory=list)
    phrasing_adjustments: list[ATSPhrasingAdjustment] = Field(default_factory=list)


class ATSOptimizerRequest(BaseModel):
    resume_id: str
    job_id: str


class ATSOptimizerResponse(ATSOptimizerResult):
    id: str
    resume_id: str
    job_id: str
    created_at: datetime
