"""
Research Router — Phase 9 Research Endpoints (Explainability traces, statistical process bias audits,
resume anomaly checks, and interview cheat risk detection).
Guarded strictly by recruiter/admin role dependencies. Automatically records audit events (Task 2).
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import require_role
from app.core.exceptions import EntityNotFoundError
from app.core.research_exceptions import AnomalyDetectionError, BiasAuditError, ExplanationTraceError
from app.models.user import User
from app.schemas.research import (
    ExplanationTraceResponse,
    InterviewCheatRiskResponse,
    ProcessBiasAuditResponse,
    ResumeAnomalyCheckResponse,
)
from app.services import research_service, audit_service

router = APIRouter(
    prefix="/research",
    tags=["Research & Explainability Features"],
    dependencies=[Depends(require_role("recruiter", "admin"))],
)


@router.get(
    "/explanation-trace",
    response_model=ExplanationTraceResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve unified explanation trace and consistency metrics",
)
async def get_unified_explanation_trace(
    candidate_id: str,
    job_id: str,
    current_user: User = Depends(require_role("recruiter", "admin")),
):
    """
    Consolidates multi-phase decision evidence (match factors, interview dimensions, code review)
    into a single trace with deterministic cross-phase consistency metrics.
    """
    try:
        return await research_service.get_unified_explanation_trace(candidate_id, job_id)
    except ExplanationTraceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get(
    "/bias-audit/{job_id}",
    response_model=ProcessBiasAuditResponse,
    status_code=status.HTTP_200_OK,
    summary="Perform statistical score distribution & process bias audit across applicant pool",
)
async def audit_job_scoring_process(
    job_id: str,
    current_user: User = Depends(require_role("recruiter", "admin")),
):
    """
    Audits score variance and factor dominance across an applicant pool for a job.
    Contains ZERO protected demographic attribute collection or profiling.
    Automatically logs an immutable audit trail entry.
    """
    try:
        res = await research_service.audit_job_scoring_process(job_id)
        await audit_service.record_audit_event(
            acting_user=current_user,
            action_type="bias_audit_query",
            target_resource_id=job_id,
            target_resource_type="job",
            decision_reason="Statistical process-level bias audit executed for applicant pool",
            details={"sample_size": res.sample_size, "variance_flag": res.high_variance_flag},
        )
        return res
    except BiasAuditError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get(
    "/resume-consistency/{resume_id}",
    response_model=ResumeAnomalyCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Check resume for timeline overlaps, unbacked skills, or contradictions",
)
async def audit_resume_internal_consistency(
    resume_id: str,
    candidate_id: str,
    current_user: User = Depends(require_role("recruiter", "admin")),
):
    """
    Audits plain-text resume for internal logic contradictions or dates overlaps.
    """
    try:
        return await research_service.audit_resume_internal_consistency(resume_id, candidate_id)
    except AnomalyDetectionError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get(
    "/cheat-risk/{session_id}",
    response_model=InterviewCheatRiskResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze stylometric consistency and cheat risk indicators across interview Q&A",
)
async def audit_interview_cheat_risk(
    session_id: str,
    candidate_id: str,
    current_user: User = Depends(require_role("recruiter", "admin")),
):
    """
    Analyzes stylometrics and phrasing shifts across interview turns.
    Outputs informational signals only; never auto-disqualifies candidates.
    """
    try:
        return await research_service.audit_interview_cheat_risk(session_id, candidate_id)
    except AnomalyDetectionError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
