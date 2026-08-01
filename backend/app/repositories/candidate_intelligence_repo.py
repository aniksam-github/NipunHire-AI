"""Persistence operations for review-only Phase 5 suggestions."""

from app.models.candidate_intelligence import ATSOptimizationSuggestion, ResumeOptimizationSuggestion


async def create_resume_suggestion(suggestion: ResumeOptimizationSuggestion) -> ResumeOptimizationSuggestion:
    return await suggestion.insert()


async def create_ats_suggestion(suggestion: ATSOptimizationSuggestion) -> ATSOptimizationSuggestion:
    return await suggestion.insert()
