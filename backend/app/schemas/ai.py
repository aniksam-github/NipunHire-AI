"""Validated, database-ready result types returned by AI features."""

from pydantic import BaseModel, Field


class ResumeAnalysis(BaseModel):
    summary: str
    skills: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)


class ResumeSummary(BaseModel):
    summary: str


class ResumeMatching(BaseModel):
    match_score: float = Field(ge=0, le=100)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class InterviewQuestions(BaseModel):
    questions: list[str] = Field(default_factory=list)


class InterviewFeedback(BaseModel):
    overall_feedback: str
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)


class CodingReview(BaseModel):
    summary: str
    strengths: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
