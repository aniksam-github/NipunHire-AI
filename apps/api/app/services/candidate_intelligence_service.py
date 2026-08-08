"""Review-only AI resume and ATS optimization workflows for Phase 5."""

import json

from beanie import PydanticObjectId

from app.ai.services.ai_service import AIService
from app.core.candidate_intelligence_exceptions import CandidateIntelligenceError
from app.core.exceptions import AuthorizationError, EntityNotFoundError
from app.models.candidate_intelligence import ATSOptimizationSuggestion, ResumeOptimizationSuggestion
from app.repositories import candidate_intelligence_repo, job_repo, resume_profile_repo, resume_repo
from app.schemas.candidate_intelligence import (
    ATSOptimizerRequest,
    ATSOptimizerResponse,
    ATSOptimizerResult,
    ResumeOptimizerRequest,
    ResumeOptimizerResponse,
    ResumeOptimizerResult,
)
from app.schemas.resume_intelligence import ResumeParsingResult
from app.services.prompt_service import load_prompt


async def _get_profile_for_candidate(resume_id: str, candidate_id: str):
    resume = await resume_repo.get_by_id(resume_id)
    if not resume:
        raise EntityNotFoundError(entity="Resume", identifier=resume_id)
    if str(resume.candidate_id) != candidate_id:
        raise AuthorizationError(detail="You can only optimize your own resume.")
    profile = await resume_profile_repo.get_by_resume_id(resume_id)
    if not profile:
        raise CandidateIntelligenceError("Resume has no parsed candidate profile.")
    return resume, profile


async def generate_resume_optimization(
    data: ResumeOptimizerRequest, candidate_id: str, ai_service: AIService | None = None
) -> ResumeOptimizerResponse:
    """Suggest rewrites without changing stored resume text or profile data."""
    resume, _ = await _get_profile_for_candidate(data.resume_id, candidate_id)
    try:
        result = await (ai_service or AIService()).get_structured_response(
            system_prompt="",
            user_prompt=load_prompt(
                "resume_optimizer",
                sections_json=json.dumps([section.model_dump() for section in data.sections]),
            ),
            response_model=ResumeOptimizerResult,
        )
    except Exception as exc:
        raise CandidateIntelligenceError("AI resume optimization failed.") from exc
    originals = [section.text for section in data.sections]
    if [rewrite.original_text for rewrite in result.rewrites] != originals:
        raise CandidateIntelligenceError("AI rewrites must preserve each submitted original text for comparison.")
    suggestion = await candidate_intelligence_repo.create_resume_suggestion(
        ResumeOptimizationSuggestion(
            candidate_id=PydanticObjectId(candidate_id), resume_id=resume.id, result=result
        )
    )
    return ResumeOptimizerResponse(id=str(suggestion.id), resume_id=str(resume.id), created_at=suggestion.created_at, **result.model_dump())


async def generate_ats_optimization(
    data: ATSOptimizerRequest, candidate_id: str, ai_service: AIService | None = None
) -> ATSOptimizerResponse:
    """Suggest job-grounded ATS changes without changing source resume data."""
    resume, profile = await _get_profile_for_candidate(data.resume_id, candidate_id)
    job = await job_repo.get_by_id(data.job_id)
    if not job:
        raise EntityNotFoundError(entity="Job", identifier=data.job_id)
    profile_data = ResumeParsingResult.model_validate(
        profile.model_dump(include={"full_name", "contact", "education", "skills", "projects", "experience"})
    )
    job_data = job.model_dump(
        mode="json",
        include={"title", "description", "department", "location", "min_experience_years", "required_skills", "optional_skills"},
    )
    try:
        result = await (ai_service or AIService()).get_structured_response(
            system_prompt="",
            user_prompt=load_prompt(
                "ats_optimizer", profile_json=json.dumps(profile_data.model_dump(mode="json")), job_json=json.dumps(job_data)
            ),
            response_model=ATSOptimizerResult,
        )
    except Exception as exc:
        raise CandidateIntelligenceError("AI ATS optimization failed.") from exc
    suggestion = await candidate_intelligence_repo.create_ats_suggestion(
        ATSOptimizationSuggestion(
            candidate_id=PydanticObjectId(candidate_id), resume_id=resume.id, job_id=job.id, result=result
        )
    )
    return ATSOptimizerResponse(
        id=str(suggestion.id), resume_id=str(resume.id), job_id=str(job.id), created_at=suggestion.created_at, **result.model_dump()
    )
