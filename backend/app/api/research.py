"""
Research Router — Phase 9 Research Endpoints (Explainability traces, statistical process bias audits,
resume anomaly checks, and interview cheat risk detection).
Guarded strictly by recruiter/admin role dependencies.
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
from app.services import research_service

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
    Contains ZERO demographic attribute collection or profiling.
    """
    try:
        return await research_service.audit_job_scoring_process(job_id)
    except BiasAuditError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post(
    "/resume-anomaly-check",
    response_model=ResumeAnomalyCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Perform internal consistency audit on candidate resume content",
)
async def check_resume_anomalies(
    candidate_id: str,
    resume_id: str,
    current_user: User = Depends(require_role("recruiter", "admin")),
):
    """
    Audits stated resume text for internal contradictions (overlapping dates, unsupported skills).
    Output is visible strictly to recruiters and labeled as a decision-support signal.
    """
    try:
        return await research_service.check_resume_anomalies(candidate_id, resume_id)
    except AnomalyDetectionError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post(
    "/interview-cheat-risk",
    response_model=InterviewCheatRiskResponse,
    status_code=status.HTTP_200_OK,
    summary="Perform stylometric anomaly detection on interview Q&A history",
)
async def detect_interview_cheat_risk(
    candidate_id: str,
    session_id: str,
    current_user: User = Depends(require_role("recruiter", "admin")),
):
    """
    Analyzes multi-turn interview Q&A history for phrasing shifts and response anomalies.
    Informational signal for human review; never auto-disqualifies a candidate.
    """
    try:
        return await research_service.detect_interview_cheat_risk(candidate_id, session_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc
    except AnomalyDetectionError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
