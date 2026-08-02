"""
Recruiter AI Router — Phase 8 recruiter-facing aggregation and decision support tools.
Guarded strictly by recruiter/admin role dependencies. Automatically records audit events (Task 2).
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import require_role
from app.core.exceptions import EntityNotFoundError
from app.core.recruiter_exceptions import (
    CandidateSummaryGenerationError,
    JobDescriptionGenerationError,
)
from app.models.user import User
from app.schemas.recruiter import (
    AggregateHiringRecommendationRequest,
    AggregateHiringRecommendationResponse,
    CandidateComparisonRequest,
    CandidateComparisonResult,
    CandidateRankingList,
    CandidateRankingRequest,
    CandidateSummaryReport,
    GeneratedJobDescription,
    JobDescriptionGenerateRequest,
    RecruiterInterviewSummaryResponse,
)
from app.services import recruiter_service, audit_service

router = APIRouter(
    prefix="/recruiter",
    tags=["Recruiter AI & Decision Support"],
    dependencies=[Depends(require_role("recruiter", "admin"))],
)


# --- Module 1: Candidate Summary ---
@router.post(
    "/candidate-summary",
    response_model=CandidateSummaryReport,
    status_code=status.HTTP_200_OK,
    summary="Generate recruiter-facing candidate summary across phase evaluations",
)
async def get_candidate_summary(
    candidate_id: str,
    job_id: str | None = None,
    current_user: User = Depends(require_role("recruiter", "admin")),
):
    """
    Synthesizes a recruiter summary from already-computed profile, match result,
    interview report, and coding review without re-running earlier AI calls.
    """
    try:
        return await recruiter_service.generate_candidate_summary(candidate_id, job_id)
    except CandidateSummaryGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


# --- Module 2: Candidate Comparison ---
@router.post(
    "/candidates/compare",
    response_model=CandidateComparisonResult,
    status_code=status.HTTP_200_OK,
    summary="Compare multiple candidates side-by-side for a target job",
)
async def compare_candidates(
    request: CandidateComparisonRequest,
    current_user: User = Depends(require_role("recruiter", "admin")),
):
    """
    Produces a side-by-side comparison matrix of candidate strengths and dimension ratings.
    """
    try:
        res = await recruiter_service.compare_candidates(request)
        await audit_service.record_audit_event(
            acting_user=current_user,
            action_type="candidate_comparison",
            target_resource_id=request.job_id,
            target_resource_type="job",
            details={"candidate_ids": request.candidate_ids},
        )
        return res
    except CandidateSummaryGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


# --- Module 3: Candidate Ranking ---
@router.post(
    "/jobs/{job_id}/rankings",
    response_model=CandidateRankingList,
    status_code=status.HTTP_200_OK,
    summary="Deterministically rank candidates for a job with AI justifications",
)
async def rank_candidates_for_job(
    job_id: str,
    request: CandidateRankingRequest | None = None,
    current_user: User = Depends(require_role("recruiter", "admin")),
):
    """
    Ranks candidates using configurable sub-score weights (match, interview, coding)
    and generates short natural language justifications per rank position.
    """
    cand_ids = request.candidate_ids if request else None
    weights = request.weights if request else None
    res = await recruiter_service.rank_candidates_for_job(job_id, cand_ids, weights)
    
    # Automatically record audit event for candidate ranking
    await audit_service.record_audit_event(
        acting_user=current_user,
        action_type="candidate_ranking",
        target_resource_id=job_id,
        target_resource_type="job",
        details={"candidate_count": len(res.rankings)},
    )
    return res


# --- Module 4: Interview Summary (Recruiter View) ---
@router.get(
    "/interviews/{session_id}/summary",
    response_model=RecruiterInterviewSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve condensed recruiter view of an interview session",
)
async def get_recruiter_interview_summary(
    session_id: str,
    current_user: User = Depends(require_role("recruiter", "admin")),
):
    """
    Returns key Q&A highlights and final report for an interview session in one view.
    """
    try:
        return await recruiter_service.get_recruiter_interview_summary(session_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc


# --- Module 5: Aggregate Hiring Recommendation ---
@router.post(
    "/recommendation",
    response_model=AggregateHiringRecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate final aggregate hiring decision (Hire/Maybe/Reject)",
)
async def generate_aggregate_hiring_recommendation(
    request: AggregateHiringRecommendationRequest,
    current_user: User = Depends(require_role("recruiter", "admin")),
):
    """
    Generates a final aggregate hiring decision grounded in candidate summary, rank, and phase data.
    Automatically logs an immutable audit event capturing the decision recommendation and reasoning.
    """
    try:
        res = await recruiter_service.generate_aggregate_hiring_recommendation(
            request.candidate_id, request.job_id
        )
        await audit_service.record_audit_event(
            acting_user=current_user,
            action_type="hiring_decision",
            target_resource_id=request.candidate_id,
            target_resource_type="candidate",
            decision_reason=f"AI Decision Recommendation: {res.recommendation}. {res.overall_reasoning}",
            details={"job_id": request.job_id, "recommendation": res.recommendation, "scores": res.scores},
        )
        return res
    except CandidateSummaryGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


# --- Module 6: Job Description Generator ---
@router.post(
    "/job-description/generate",
    response_model=GeneratedJobDescription,
    status_code=status.HTTP_201_CREATED,
    summary="Generate structured job description for recruiters",
)
async def generate_job_description(
    request: JobDescriptionGenerateRequest,
    current_user: User = Depends(require_role("recruiter", "admin")),
):
    """
    Generates structured role responsibilities and qualifications for a new job posting.
    """
    try:
        return await recruiter_service.generate_job_description(request)
    except JobDescriptionGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
