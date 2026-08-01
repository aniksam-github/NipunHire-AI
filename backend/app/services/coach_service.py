"""Career-coach Q&A and review-only AI career-plan history."""

import json

from beanie import PydanticObjectId

from app.ai.services.ai_service import AIService
from app.core.candidate_intelligence_exceptions import CandidateIntelligenceError
from app.core.exceptions import EntityNotFoundError
from app.models.coach import CoachMessage
from app.repositories import coach_repo, matching_repo, resume_profile_repo, resume_repo, resume_screening_repo
from app.schemas.candidate_intelligence import (
    CareerCoachAnalysisRequest,
    CareerCoachAnalysisResponse,
    CareerCoachResult,
)
from app.schemas.coach import CoachMessageResponse, CoachQuestion, CoachPlanHistoryResponse
from app.schemas.resume_intelligence import ResumeParsingResult
from app.services.prompt_service import load_prompt


def _answer(question: str) -> str:
    lower = question.lower()
    if "resume" in lower:
        return "Start with the role you want, then make each bullet show action, scope, and a measurable outcome. Use the Resume Center scorecard to prioritise missing keywords."
    if "interview" in lower:
        return "Choose one target role, practise three questions, and answer with Situation, Task, Action, Result. Review the score and improve one specific point in the next session."
    if "skill" in lower or "learn" in lower:
        return "Pick one skill gap connected to target jobs, build a small project around it, document the result, then add that evidence to your resume and portfolio."
    return "Break this into a one-week goal: define the target outcome, choose one measurable action each day, and review your progress at the end of the week."


def _response(message: CoachMessage) -> CoachMessageResponse:
    return CoachMessageResponse(id=str(message.id), question=message.question, answer=message.answer, created_at=message.created_at)


async def ask(candidate_id: str, data: CoachQuestion) -> CoachMessageResponse:
    message = CoachMessage(candidate_id=PydanticObjectId(candidate_id), question=data.question, answer=_answer(data.question))
    await coach_repo.create(message)
    return _response(message)


async def history(candidate_id: str) -> list[CoachMessageResponse]:
    rows = await coach_repo.list_by_candidate(candidate_id)
    return [_response(row) for row in rows]


async def _get_candidate_profile(candidate_id: str, resume_id: str | None):
    if resume_id:
        resume = await resume_repo.get_by_id(resume_id)
        if not resume or str(resume.candidate_id) != candidate_id:
            raise EntityNotFoundError(entity="Resume", identifier=resume_id)
        profile = await resume_profile_repo.get_by_resume_id(resume_id)
        if not profile:
            raise CandidateIntelligenceError("Resume has no parsed candidate profile.")
        return resume, profile
    for resume in await resume_repo.list_by_candidate(candidate_id):
        profile = await resume_profile_repo.get_by_resume_id(str(resume.id))
        if profile:
            return resume, profile
    raise CandidateIntelligenceError("No parsed resume is available for career coaching.")


async def generate_plan(
    candidate_id: str,
    data: CareerCoachAnalysisRequest,
    ai_service: AIService | None = None,
) -> CareerCoachAnalysisResponse:
    """Create a persisted, AI-generated plan from existing candidate intelligence."""
    resume, profile = await _get_candidate_profile(candidate_id, data.resume_id)
    screening = await resume_screening_repo.get_by_profile_id(str(profile.id))
    profile_data = ResumeParsingResult.model_validate(
        profile.model_dump(include={"full_name", "contact", "education", "skills", "projects", "experience"})
    )
    screening_data = screening.model_dump(include={"analysis", "skills", "improvements"}) if screening else {}
    matches = await matching_repo.list_recent_by_candidate(candidate_id)
    match_data = [
        match.model_dump(
            mode="json",
            include={"match_score", "missing_required_skills", "strengths", "weaknesses", "explainable_result"},
        )
        for match in matches
    ]
    try:
        result = await (ai_service or AIService()).get_structured_response(
            system_prompt="",
            user_prompt=load_prompt(
                "career_coach",
                profile_json=json.dumps(profile_data.model_dump(mode="json")),
                screening_json=json.dumps(screening_data, default=str),
                matches_json=json.dumps(match_data, default=str),
            ),
            response_model=CareerCoachResult,
        )
    except Exception as exc:
        raise CandidateIntelligenceError("AI career-plan generation failed.") from exc
    message = await coach_repo.create(
        CoachMessage(
            candidate_id=PydanticObjectId(candidate_id),
            resume_id=resume.id,
            question="AI career plan",
            answer=result.career_advice,
            career_plan=result,
        )
    )
    return CareerCoachAnalysisResponse(
        id=str(message.id), resume_id=str(resume.id), created_at=message.created_at, **result.model_dump()
    )


async def plan_history(candidate_id: str) -> list[CoachPlanHistoryResponse]:
    return [
        CoachPlanHistoryResponse(
            id=str(row.id),
            question=row.question,
            answer=row.answer,
            created_at=row.created_at,
            career_plan=row.career_plan,
            resume_id=str(row.resume_id) if row.resume_id else None,
        )
        for row in await coach_repo.list_by_candidate(candidate_id)
    ]
