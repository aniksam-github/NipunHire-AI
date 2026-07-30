"""Explainable, profile-to-job resume matching for Phase 4.

Scores are represented by named factor contributions rather than a black-box
percentage so recruiters can audit each gain/loss and researchers can evaluate
the model's stated evidence independently of the final recommendation.
"""

import json
import logging

from app.ai.services.ai_service import AIService
from app.ai.utils.token_utils import estimate_token_count
from app.core.config import settings
from app.core.exceptions import AuthorizationError, EntityNotFoundError
from app.core.matching_exceptions import ResumeMatchingError
from app.models.matching import JobMatch
from app.repositories import job_repo, matching_repo, resume_profile_repo, resume_repo
from app.schemas.resume_intelligence import ResumeParsingResult
from app.schemas.resume_matching import (
    BaseMatchResult,
    ExplainableMatchResponse,
    MatchRecommendation,
    RecruiterRecommendation,
)
from app.services.prompt_service import load_prompt

logger = logging.getLogger(__name__)


def _profile_json(profile: ResumeParsingResult) -> str:
    return json.dumps(profile.model_dump(mode="json"))


async def analyze_match(
    profile: ResumeParsingResult, job_details: dict[str, object], ai_service: AIService
) -> BaseMatchResult:
    """Use AI once to produce the score and its auditable factor breakdown."""
    prompt = load_prompt(
        "resume_matching",
        profile_json=_profile_json(profile),
        job_json=json.dumps(job_details),
    )
    logger.info(
        "Prepared explainable AI match request",
        extra={"stage": "matching", "estimated_prompt_tokens": estimate_token_count(prompt, settings.OPENAI_MODEL)},
    )
    try:
        response = await ai_service.get_structured_response(
            system_prompt="",
            user_prompt=prompt,
            response_model=BaseMatchResult,
        )
        # Revalidate even a mocked/preconstructed model before persistence.
        return BaseMatchResult.model_validate(response.model_dump())
    except Exception as exc:
        raise ResumeMatchingError("AI resume matching failed") from exc


def derive_recommendation(result: BaseMatchResult) -> MatchRecommendation:
    """Derive a traceable recommendation from the already-audited factors.

    This intentionally does not make a second AI call: the recommendation is
    reproducible from the same evidence recruiters inspect, avoiding both
    redundant cost and an untraceable second model judgement.
    """
    largest_gap = min(result.factors, key=lambda factor: factor.point_contribution)
    if result.overall_match_percentage >= 75 and largest_gap.point_contribution > -25:
        recommendation = RecruiterRecommendation.HIRE
    elif result.overall_match_percentage >= 50:
        recommendation = RecruiterRecommendation.MAYBE
    else:
        recommendation = RecruiterRecommendation.REJECT
    return MatchRecommendation(
        recommendation=recommendation,
        reason=(
            f"Match score is {result.overall_match_percentage}%. "
            f"Most significant gap: {largest_gap.name} "
            f"({largest_gap.point_contribution:+d} points) because {largest_gap.reason}"
        ),
    )


async def match_resume_to_job(
    candidate_id: str,
    job_id: str,
    resume_id: str | None = None,
    ai_service: AIService | None = None,
) -> ExplainableMatchResponse:
    """Match one parsed candidate profile to an existing job and persist it."""
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise EntityNotFoundError(entity="Job", identifier=job_id)
    resume = await resume_repo.get_by_id(resume_id) if resume_id else None
    if resume is None:
        resumes = await resume_repo.list_by_candidate(candidate_id)
        resume = next((item for item in resumes if item.profile_id), None)
    if not resume:
        raise ResumeMatchingError("No parsed resume is available for matching.")
    if str(resume.candidate_id) != candidate_id:
        raise AuthorizationError(detail="You can only match your own uploaded resume.")
    profile_document = await resume_profile_repo.get_by_resume_id(str(resume.id))
    if not profile_document:
        raise ResumeMatchingError("Resume has no parsed candidate profile to match.")

    profile = ResumeParsingResult.model_validate(
        profile_document.model_dump(
            include={"full_name", "contact", "education", "skills", "projects", "experience"}
        )
    )
    job_details = job.model_dump(
        mode="json",
        include={"title", "description", "department", "location", "min_experience_years", "required_skills", "optional_skills"},
    )
    result = await analyze_match(profile, job_details, ai_service or AIService())
    recommendation = derive_recommendation(result)

    existing = await matching_repo.get_by_candidate_and_job(candidate_id, job_id)
    if existing:
        match = existing
        match.resume_id = resume.id
        match.profile_id = profile_document.id
        match.match_score = result.overall_match_percentage
        match.missing_required_skills = result.missing_skills
        match.strengths = [factor.reason for factor in result.factors if factor.point_contribution > 0]
        match.weaknesses = [factor.reason for factor in result.factors if factor.point_contribution < 0]
        match.application_readiness_score = result.overall_match_percentage
        match.recommendations = [recommendation.reason]
        match.explainable_result = result
        match.recruiter_recommendation = recommendation
        await match.save()
    else:
        match = await matching_repo.create(
            JobMatch(
                candidate_id=resume.candidate_id,
                job_id=job.id,
                resume_id=resume.id,
                profile_id=profile_document.id,
                match_score=result.overall_match_percentage,
                missing_required_skills=result.missing_skills,
                strengths=[factor.reason for factor in result.factors if factor.point_contribution > 0],
                weaknesses=[factor.reason for factor in result.factors if factor.point_contribution < 0],
                application_readiness_score=result.overall_match_percentage,
                recommendations=[recommendation.reason],
                explainable_result=result,
                recruiter_recommendation=recommendation,
            )
        )

    logger.info("Explainable resume match completed", extra={"job_id": job_id, "resume_id": str(resume.id)})
    return ExplainableMatchResponse(
        id=str(match.id),
        profile_id=str(profile_document.id),
        job_id=job_id,
        result=result,
        recommendation=recommendation,
    )
