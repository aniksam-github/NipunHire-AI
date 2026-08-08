"""Phase 3 orchestration for analysis of an already-parsed resume profile."""

import json
import logging
from datetime import datetime, timezone

from app.ai.services.ai_service import AIService
from app.ai.utils.token_utils import estimate_token_count
from app.core.config import settings
from app.core.exceptions import AuthorizationError, EntityNotFoundError
from app.core.screening_exceptions import ResumeScreeningError
from app.models.resume_screening import ResumeScreening
from app.repositories import resume_profile_repo, resume_repo, resume_screening_repo
from app.schemas.resume_intelligence import ResumeParsingResult
from app.schemas.resume_screening import (
    CategorizedSkillsResult,
    ResumeAnalysisResult,
    ResumeImprovementResult,
    ResumeScreeningResponse,
)
from app.services.prompt_service import load_prompt

logger = logging.getLogger(__name__)


def _profile_json(profile: ResumeParsingResult) -> str:
    """Serialize only parsed candidate facts, not raw resume text or DB metadata."""
    return json.dumps(profile.model_dump(mode="json"))


async def analyze_profile(
    profile: ResumeParsingResult, ai_service: AIService
) -> ResumeAnalysisResult:
    """Generate a validated assessment from a structured candidate profile."""
    prompt = load_prompt("resume_analysis", profile_json=_profile_json(profile))
    logger.info(
        "Prepared AI resume analysis request",
        extra={"stage": "analysis", "estimated_prompt_tokens": estimate_token_count(prompt, settings.OPENAI_MODEL)},
    )
    try:
        return await ai_service.get_structured_response(
            system_prompt="",
            user_prompt=prompt,
            response_model=ResumeAnalysisResult,
        )
    except Exception as exc:
        raise ResumeScreeningError("AI resume analysis failed") from exc


async def extract_categorized_skills(
    profile: ResumeParsingResult, ai_service: AIService
) -> CategorizedSkillsResult:
    """Generate a validated categorized skill breakdown from a structured profile."""
    prompt = load_prompt("skill_extraction", profile_json=_profile_json(profile))
    logger.info(
        "Prepared AI skill extraction request",
        extra={"stage": "skill_extraction", "estimated_prompt_tokens": estimate_token_count(prompt, settings.OPENAI_MODEL)},
    )
    try:
        return await ai_service.get_structured_response(
            system_prompt="",
            user_prompt=prompt,
            response_model=CategorizedSkillsResult,
        )
    except Exception as exc:
        raise ResumeScreeningError("AI skill extraction failed") from exc


async def generate_improvements(
    profile: ResumeParsingResult,
    analysis: ResumeAnalysisResult,
    skills: CategorizedSkillsResult,
    ai_service: AIService,
) -> ResumeImprovementResult:
    """Generate improvements from already-computed analysis and categorized skills."""
    prompt = load_prompt(
        "resume_improvement",
        profile_json=_profile_json(profile),
        analysis_json=json.dumps(analysis.model_dump(mode="json")),
        skills_json=json.dumps(skills.model_dump(mode="json")),
    )
    logger.info(
        "Prepared AI resume improvement request",
        extra={"stage": "improvement", "estimated_prompt_tokens": estimate_token_count(prompt, settings.OPENAI_MODEL)},
    )
    try:
        return await ai_service.get_structured_response(
            system_prompt="",
            user_prompt=prompt,
            response_model=ResumeImprovementResult,
        )
    except Exception as exc:
        raise ResumeScreeningError("AI resume improvement generation failed") from exc


async def screen_resume(
    resume_id: str, candidate_id: str, ai_service: AIService | None = None
) -> ResumeScreeningResponse:
    """Run Phase 3 sequentially and persist all outputs against the profile."""
    resume = await resume_repo.get_by_id(resume_id)
    if not resume:
        raise EntityNotFoundError(entity="Resume", identifier=resume_id)
    if str(resume.candidate_id) != candidate_id:
        raise AuthorizationError(detail="You can only screen your own uploaded resumes.")
    profile_document = await resume_profile_repo.get_by_resume_id(resume_id)
    if not profile_document:
        raise ResumeScreeningError("Resume has no parsed candidate profile to screen.")

    parsed_profile = ResumeParsingResult.model_validate(
        profile_document.model_dump(
            include={"full_name", "contact", "education", "skills", "projects", "experience"}
        )
    )
    client = ai_service or AIService()
    analysis = await analyze_profile(parsed_profile, client)
    skills = await extract_categorized_skills(parsed_profile, client)
    improvements = await generate_improvements(parsed_profile, analysis, skills, client)

    screening = await resume_screening_repo.get_by_profile_id(str(profile_document.id))
    if screening:
        screening.analysis = analysis
        screening.skills = skills
        screening.improvements = improvements
        screening.updated_at = datetime.now(timezone.utc)
        await resume_screening_repo.save(screening)
    else:
        screening = await resume_screening_repo.create(
            ResumeScreening(
                profile_id=profile_document.id,
                resume_id=resume.id,
                candidate_id=resume.candidate_id,
                analysis=analysis,
                skills=skills,
                improvements=improvements,
            )
        )

    logger.info("Resume screening completed", extra={"resume_id": resume_id, "profile_id": str(profile_document.id)})
    return ResumeScreeningResponse(
        profile_id=str(profile_document.id),
        analysis=screening.analysis,
        skills=screening.skills,
        improvements=screening.improvements,
    )
