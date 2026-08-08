"""
Agent Tools Registry — Tool schemas and server-side execution wrappers for AI Career Assistant.
"""

import json
import logging
from typing import Any

from app.ai.services.ai_service import AIService
from app.core.exceptions import EntityNotFoundError
from app.repositories import job_repo, resume_profile_repo, resume_repo
from app.schemas.candidate_intelligence import ATSOptimizerRequest, CareerCoachAnalysisRequest
from app.schemas.resume_intelligence import ResumeParsingResult
from app.services import candidate_intelligence_service, coach_service, resume_screening_service

logger = logging.getLogger(__name__)

# ---- OpenAI Function / Tool Definitions ----
CAREER_ASSISTANT_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "screen_and_analyze_resume",
            "description": "Performs comprehensive candidate resume screening and holistic analysis to evaluate strengths, weaknesses, and overall role readiness.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "extract_skills_and_gaps",
            "description": "Extracts technical, soft, and domain skills from candidate profile and identifies skill gaps.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_resume_improvement_suggestions",
            "description": "Generates concrete resume improvement suggestions, bullet rewrites, and formatting tips.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "optimize_ats_for_job",
            "description": "Evaluates ATS keyword match rate and recommended keyword additions for the target job or role.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_role": {
                        "type": "string",
                        "description": "Optional target job title or role name.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_career_coaching_plan",
            "description": "Generates a personalized career coaching plan with skill development milestones and 30/60/90 day action items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_role": {
                        "type": "string",
                        "description": "Optional target role name.",
                    }
                },
                "required": [],
            },
        },
    },
]


async def _resolve_candidate_profile(
    candidate_id: str, request_resume_id: str | None = None
) -> tuple[Any, ResumeParsingResult]:
    """
    Server-side helper: Resolves candidate's resume and parsed profile.
    Ignores model hallucinated IDs; strictly enforces authenticated candidate scope.
    """
    if request_resume_id:
        resume = await resume_repo.get_by_id(request_resume_id)
        if not resume or str(resume.candidate_id) != candidate_id:
            raise EntityNotFoundError(entity="Resume", identifier=request_resume_id)
        profile_doc = await resume_profile_repo.get_by_resume_id(request_resume_id)
        if not profile_doc:
            raise ValueError("Resume has no parsed profile available.")
    else:
        resumes = await resume_repo.list_by_candidate(candidate_id)
        if not resumes:
            raise ValueError("No uploaded resume found for candidate.")
        resume = resumes[0]
        profile_doc = await resume_profile_repo.get_by_resume_id(str(resume.id))
        if not profile_doc:
            raise ValueError("Candidate resume has no parsed profile available.")

    profile = ResumeParsingResult.model_validate(
        profile_doc.model_dump(
            include={"full_name", "contact", "education", "skills", "projects", "experience"}
        )
    )
    return resume, profile


async def execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
    candidate_id: str,
    request_resume_id: str | None = None,
    request_job_id: str | None = None,
    ai_service: AIService | None = None,
) -> dict[str, Any]:
    """
    Executes a requested tool safely.
    Catches execution errors gracefully and enforces server-side authenticated context locking.
    """
    client = ai_service or AIService()

    try:
        if tool_name == "screen_and_analyze_resume":
            resume, profile = await _resolve_candidate_profile(candidate_id, request_resume_id)
            result = await resume_screening_service.analyze_profile(profile, client)
            return {"status": "success", "tool": tool_name, "data": result.model_dump(mode="json")}

        elif tool_name == "extract_skills_and_gaps":
            resume, profile = await _resolve_candidate_profile(candidate_id, request_resume_id)
            result = await resume_screening_service.extract_categorized_skills(profile, client)
            return {"status": "success", "tool": tool_name, "data": result.model_dump(mode="json")}

        elif tool_name == "get_resume_improvement_suggestions":
            resume, profile = await _resolve_candidate_profile(candidate_id, request_resume_id)
            result = await resume_screening_service.suggest_resume_improvements(profile, client)
            return {"status": "success", "tool": tool_name, "data": result.model_dump(mode="json")}

        elif tool_name == "optimize_ats_for_job":
            resume, profile = await _resolve_candidate_profile(candidate_id, request_resume_id)
            job_id = request_job_id
            target_role = arguments.get("target_role") or "Software Engineer"
            if job_id:
                job = await job_repo.get_by_id(job_id)
                if job:
                    target_role = job.title

            req = ATSOptimizerRequest(resume_id=str(resume.id), job_id=job_id, target_role=target_role)
            result = await candidate_intelligence_service.generate_ats_optimization(req, candidate_id, client)
            return {"status": "success", "tool": tool_name, "data": result.model_dump(mode="json")}

        elif tool_name == "get_career_coaching_plan":
            resume, _ = await _resolve_candidate_profile(candidate_id, request_resume_id)
            target_role = arguments.get("target_role") or "Senior Developer"
            req = CareerCoachAnalysisRequest(resume_id=str(resume.id), target_role=target_role)
            result = await coach_service.generate_plan(candidate_id, req, client)
            return {"status": "success", "tool": tool_name, "data": result.model_dump(mode="json")}

        else:
            return {
                "status": "error",
                "tool": tool_name,
                "error": f"Unknown tool name '{tool_name}'.",
                "message": "Available tools are: screen_and_analyze_resume, extract_skills_and_gaps, get_resume_improvement_suggestions, optimize_ats_for_job, get_career_coaching_plan.",
            }

    except Exception as exc:
        logger.warning("Tool execution error in %s for candidate %s: %s", tool_name, candidate_id, exc)
        return {
            "status": "error",
            "tool": tool_name,
            "error": str(exc),
            "message": f"Execution of {tool_name} failed. You may select another tool or answer the candidate using existing information.",
        }
