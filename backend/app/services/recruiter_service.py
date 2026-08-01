"""
Phase 8 Recruiter AI Service — Candidate summary aggregation, candidate comparison,
deterministic candidate ranking, recruiter interview view, aggregate hiring recommendation,
and job description generation.
"""

import json
import logging
from typing import Any

from beanie import PydanticObjectId
from pydantic import BaseModel

from app.ai.services.ai_service import AIService
from app.core.exceptions import EntityNotFoundError
from app.core.recruiter_exceptions import (
    CandidateSummaryGenerationError,
    JobDescriptionGenerationError,
)
from app.repositories import (
    coding_repo,
    interview_repo,
    job_repo,
    matching_repo,
    profile_repo,
    resume_profile_repo,
    resume_repo,
)
from app.schemas.interview import InterviewReport
from app.schemas.recruiter import (
    AggregateHiringRecommendationRequest,
    AggregateHiringRecommendationResponse,
    CandidateComparisonEntry,
    CandidateComparisonRequest,
    CandidateComparisonResult,
    CandidateRankingList,
    CandidateSummaryReport,
    GeneratedJobDescription,
    JobDescriptionGenerateRequest,
    RankedCandidateEntry,
    RankingWeights,
    RecruiterInterviewHighlight,
    RecruiterInterviewSummaryResponse,
)
from app.schemas.resume_matching import RecruiterRecommendation
from app.services.prompt_service import load_prompt

logger = logging.getLogger(__name__)


class RankingJustificationResult(BaseModel):
    justification: str


# --- Helper Context Retrievers ---
async def _get_candidate_context_bundle(candidate_id: str, job_id: str | None = None) -> dict[str, Any]:
    """Fetches already-computed data (profile, match, interview, coding) for a candidate without running AI."""
    profile_str = "{}"
    try:
        resumes = await resume_repo.list_by_candidate(candidate_id)
        if resumes:
            for res in resumes:
                if res.profile_id:
                    resume_prof = await resume_profile_repo.get_by_resume_id(str(res.id))
                    if resume_prof:
                        profile_str = json.dumps(
                            resume_prof.model_dump(
                                mode="json",
                                include={"full_name", "skills", "experience", "education", "projects", "professional_summary"},
                            )
                        )
                        break
        if profile_str == "{}":
            profile = await profile_repo.get_by_candidate(candidate_id)
            if profile:
                profile_str = json.dumps(
                    profile.model_dump(
                        mode="json",
                        include={"headline", "bio", "skills", "experience", "education", "projects"},
                    )
                )
    except Exception as exc:
        logger.warning("Could not fetch profile context for %s: %s", candidate_id, exc)

    # Match Result (Phase 4)
    match_dict = {}
    if job_id:
        match_doc = await matching_repo.get_by_candidate_and_job(candidate_id, job_id)
        if match_doc:
            match_dict = match_doc.model_dump(mode="json", include={"match_score", "explainable_result", "recruiter_recommendation"})
    if not match_dict:
        matches = await matching_repo.list_recent_by_candidate(candidate_id, limit=1)
        if matches:
            match_dict = matches[0].model_dump(mode="json", include={"match_score", "explainable_result", "recruiter_recommendation"})

    # Interview Report (Phase 6)
    interview_dict = {}
    sessions = await interview_repo.list_sessions_by_candidate(candidate_id, limit=5)
    if sessions:
        valid_sessions = [s for s in sessions if s.final_report]
        target_session = valid_sessions[0] if valid_sessions else sessions[0]
        interview_dict = target_session.model_dump(
            mode="json",
            include={"overall_score", "status", "current_difficulty", "final_report"},
        )

    # Coding Review (Phase 7)
    coding_dict = {}
    submissions = await coding_repo.list_submissions_by_candidate(candidate_id, limit=5)
    if submissions:
        valid_subs = [sub for sub in submissions if sub.review]
        target_sub = valid_subs[0] if valid_subs else submissions[0]
        coding_dict = target_sub.model_dump(
            mode="json",
            include={"language", "difficulty", "overall_score", "correctness_score", "code_quality_score", "review"},
        )

    return {
        "candidate_id": candidate_id,
        "profile_json": profile_str,
        "match_json": json.dumps(match_dict) if match_dict else "None",
        "interview_json": json.dumps(interview_dict) if interview_dict else "None",
        "coding_json": json.dumps(coding_dict) if coding_dict else "None",
        "raw_match": match_dict,
        "raw_interview": interview_dict,
        "raw_coding": coding_dict,
    }


# --- Module 1: Candidate Summary ---
async def generate_candidate_summary(
    candidate_id: str,
    job_id: str | None = None,
    ai_service: AIService | None = None,
) -> CandidateSummaryReport:
    """Synthesizes a recruiter-facing summary from candidate's existing structured data."""
    ai = ai_service or AIService()
    bundle = await _get_candidate_context_bundle(candidate_id, job_id)

    prompt = load_prompt(
        "candidate_summary_report",
        candidate_profile=bundle["profile_json"],
        match_result=bundle["match_json"],
        interview_report=bundle["interview_json"],
        coding_review=bundle["coding_json"],
    )

    try:
        summary = await ai.get_structured_response(
            system_prompt="You are a senior recruiter synthesizing candidate evaluation data.",
            user_prompt=prompt,
            response_model=CandidateSummaryReport,
        )
        summary.candidate_id = candidate_id
        return summary
    except Exception as exc:
        logger.error("Failed to generate candidate summary: %s", exc)
        raise CandidateSummaryGenerationError("Failed to generate candidate summary via AI") from exc


# --- Module 2: Candidate Comparison ---
async def compare_candidates(
    request: CandidateComparisonRequest,
    ai_service: AIService | None = None,
) -> CandidateComparisonResult:
    """Takes existing summaries/scores for multiple candidates and returns a side-by-side comparison."""
    ai = ai_service or AIService()
    job = await job_repo.get_by_id(request.job_id)
    job_details_str = json.dumps(
        job.model_dump(mode="json", include={"title", "department", "required_skills"}) if job else {"id": request.job_id}
    )

    candidate_bundles = []
    for c_id in request.candidate_ids:
        bundle = await _get_candidate_context_bundle(c_id, request.job_id)
        candidate_bundles.append(
            {
                "candidate_id": c_id,
                "profile": bundle["profile_json"],
                "match": bundle["raw_match"],
                "interview": bundle["raw_interview"],
                "coding": bundle["raw_coding"],
            }
        )

    prompt = load_prompt(
        "candidate_comparison",
        job_details=job_details_str,
        candidates_data_json=json.dumps(candidate_bundles),
    )

    try:
        res = await ai.get_structured_response(
            system_prompt="You are a recruiting director performing a side-by-side candidate comparison.",
            user_prompt=prompt,
            response_model=CandidateComparisonResult,
        )
        res.job_id = request.job_id
        res.candidates_compared = request.candidate_ids
        return res
    except Exception as exc:
        logger.error("Failed to compare candidates: %s", exc)
        raise CandidateSummaryGenerationError("Failed to compare candidates via AI") from exc


# --- Module 3: Candidate Ranking (Deterministic Logic) ---
def compute_deterministic_composite_score(
    sub_scores: dict[str, float | None],
    weights: RankingWeights,
) -> float:
    """
    Pure deterministic calculation that scores candidates using available sub-scores.
    Dynamically normalizes weights if some phase scores are missing.
    """
    score_map = {
        "match": (sub_scores.get("match_score"), weights.match_weight),
        "interview": (sub_scores.get("interview_score"), weights.interview_weight),
        "coding": (sub_scores.get("coding_score"), weights.coding_weight),
    }

    available_pairs = [(val, w) for val, w in score_map.values() if val is not None]
    if not available_pairs:
        return 0.0

    total_available_weight = sum(w for _, w in available_pairs)
    if total_available_weight <= 0:
        return 0.0

    weighted_sum = sum(val * (w / total_available_weight) for val, w in available_pairs)
    return round(weighted_sum, 2)


async def rank_candidates_for_job(
    job_id: str,
    candidate_ids: list[str] | None = None,
    weights: RankingWeights | None = None,
    ai_service: AIService | None = None,
) -> CandidateRankingList:
    """
    Ranks candidates using deterministic score calculation with dynamic weight normalization,
    and generates concise AI justifications per rank position.
    """
    ai = ai_service or AIService()
    effective_weights = weights or RankingWeights()

    target_candidate_ids = candidate_ids
    if not target_candidate_ids:
        # Query candidates who matched or applied for job_id
        matches = await matching_repo.list_recent_by_candidate("", limit=50)  # query job matches if available
        job_matches = [m for m in matches if str(m.job_id) == job_id]
        target_candidate_ids = list({str(m.candidate_id) for m in job_matches})

    if not target_candidate_ids:
        return CandidateRankingList(job_id=job_id, weights_used=effective_weights, rankings=[])

    job = await job_repo.get_by_id(job_id)
    job_title = job.title if job else "Target Position"

    evaluated_candidates = []

    for c_id in target_candidate_ids:
        bundle = await _get_candidate_context_bundle(c_id, job_id)
        raw_match = bundle["raw_match"]
        raw_interview = bundle["raw_interview"]
        raw_coding = bundle["raw_coding"]

        m_score = float(raw_match["match_score"]) if raw_match and "match_score" in raw_match else None
        i_score = float(raw_interview["overall_score"]) if raw_interview and raw_interview.get("overall_score") is not None else None
        c_score = float(raw_coding["overall_score"]) if raw_coding and raw_coding.get("overall_score") is not None else None

        sub_scores = {
            "match_score": m_score,
            "interview_score": i_score,
            "coding_score": c_score,
        }

        comp_score = compute_deterministic_composite_score(sub_scores, effective_weights)
        evaluated_candidates.append({
            "candidate_id": c_id,
            "composite_score": comp_score,
            "sub_scores": sub_scores,
            "summary_snippet": bundle["profile_json"],
        })

    # Deterministic sorting: descending order by composite_score
    evaluated_candidates.sort(key=lambda x: x["composite_score"], reverse=True)

    rankings = []
    for idx, cand in enumerate(evaluated_candidates, start=1):
        # AI call for short rank justification based on computed scores
        prompt = load_prompt(
            "ranking_justification",
            job_title=job_title,
            rank=idx,
            composite_score=cand["composite_score"],
            sub_scores_json=json.dumps(cand["sub_scores"]),
            candidate_summary=cand["summary_snippet"],
        )
        try:
            just_res = await ai.get_structured_response(
                system_prompt="You are a lead recruiter providing rank justifications.",
                user_prompt=prompt,
                response_model=RankingJustificationResult,
            )
            justification = just_res.justification
        except Exception:
            justification = f"Ranked #{idx} with composite score of {cand['composite_score']}/100."

        rankings.append(
            RankedCandidateEntry(
                rank=idx,
                candidate_id=cand["candidate_id"],
                composite_score=cand["composite_score"],
                sub_scores=cand["sub_scores"],
                justification=justification,
            )
        )

    return CandidateRankingList(
        job_id=job_id,
        weights_used=effective_weights,
        rankings=rankings,
    )


# --- Module 4: Interview Summary (Recruiter View) ---
async def get_recruiter_interview_summary(session_id: str) -> RecruiterInterviewSummaryResponse:
    """Returns a condensed view of a candidate's full interview session for recruiters."""
    session = await interview_repo.get_session_by_id(session_id)
    if not session:
        raise EntityNotFoundError(entity="Interview session", identifier=session_id)

    highlights = []
    for turn in session.turns:
        answer_text = turn.candidate_answer.strip()
        summary_text = (answer_text[:147] + "...") if len(answer_text) > 150 else answer_text
        highlights.append(
            RecruiterInterviewHighlight(
                turn_index=turn.turn_index,
                question_text=turn.question.question_text,
                category=turn.question.category.value,
                candidate_answer_summary=summary_text,
                turn_score=turn.evaluation.overall_turn_score,
            )
        )

    final_rep = InterviewReport.model_validate(session.final_report.model_dump()) if session.final_report else None

    return RecruiterInterviewSummaryResponse(
        session_id=str(session.id),
        candidate_id=str(session.candidate_id),
        job_id=str(session.job_id) if session.job_id else None,
        overall_score=session.overall_score,
        hiring_recommendation=session.final_report.hiring_recommendation.value if session.final_report else None,
        status=session.status.value,
        key_qa_highlights=highlights,
        final_report=final_rep,
    )


# --- Module 5: Aggregate Hiring Recommendation ---
async def generate_aggregate_hiring_recommendation(
    candidate_id: str,
    job_id: str | None = None,
    ai_service: AIService | None = None,
) -> AggregateHiringRecommendationResponse:
    """Produces one final aggregate hiring decision (Hire/Maybe/Reject) grounded in all phase data."""
    ai = ai_service or AIService()
    bundle = await _get_candidate_context_bundle(candidate_id, job_id)

    job_details_str = "General role"
    rank_pos = "N/A"
    if job_id:
        job = await job_repo.get_by_id(job_id)
        if job:
            job_details_str = json.dumps(job.model_dump(mode="json", include={"title", "department", "required_skills"}))

    summary_rep = await generate_candidate_summary(candidate_id, job_id, ai)
    summary_str = json.dumps(summary_rep.model_dump(mode="json"))

    scores_summary = {
        "match_score": bundle["raw_match"].get("match_score") if bundle["raw_match"] else None,
        "interview_score": bundle["raw_interview"].get("overall_score") if bundle["raw_interview"] else None,
        "coding_score": bundle["raw_coding"].get("overall_score") if bundle["raw_coding"] else None,
    }

    prompt = load_prompt(
        "aggregate_hiring_recommendation",
        job_details=job_details_str,
        candidate_summary=summary_str,
        rank_position=rank_pos,
        scores_json=json.dumps(scores_summary),
        interview_report=bundle["interview_json"],
        coding_review=bundle["coding_json"],
    )

    try:
        res = await ai.get_structured_response(
            system_prompt="You are an executive hiring panel chair issuing a final aggregate hiring decision.",
            user_prompt=prompt,
            response_model=AggregateHiringRecommendationResponse,
        )
        res.candidate_id = candidate_id
        res.job_id = job_id
        return res
    except Exception as exc:
        logger.error("Failed to generate aggregate hiring recommendation: %s", exc)
        raise CandidateSummaryGenerationError("Failed to generate aggregate hiring recommendation via AI") from exc


# --- Module 6: Job Description Generator ---
async def generate_job_description(
    request: JobDescriptionGenerateRequest,
    ai_service: AIService | None = None,
) -> GeneratedJobDescription:
    """Generates a structured job description (responsibilities, qualifications, summary)."""
    ai = ai_service or AIService()
    prompt = load_prompt(
        "job_description_generator",
        role_title=request.role_title,
        seniority_level=request.seniority_level,
        required_skills=", ".join(request.required_skills),
    )
    try:
        return await ai.get_structured_response(
            system_prompt="You are a talent acquisition manager creating a job description.",
            user_prompt=prompt,
            response_model=GeneratedJobDescription,
        )
    except Exception as exc:
        logger.error("Failed to generate job description: %s", exc)
        raise JobDescriptionGenerationError("Failed to generate job description via AI") from exc
