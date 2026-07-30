"""
Matching API Router — job description vs resume matching & skill gap analysis endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.dependencies import get_current_user
from app.core.exceptions import AuthorizationError, EntityNotFoundError
from app.core.matching_exceptions import ResumeMatchingError
from app.models.user import User
from app.schemas.matching import MatchRequest, MatchResponse
from app.services import matching_service
from app.services import resume_matching_service
from app.schemas.resume_matching import ExplainableMatchResponse

router = APIRouter(prefix="/matching", tags=["Job Matching"])


@router.post(
    "/compare",
    response_model=MatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare candidate resume against a Job Description",
)
async def compare_resume_with_job(
    data: MatchRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Evaluates candidate's skills against job requirements, returning a Match Score,
    Skill Gap list, and Application Readiness evaluation.
    """
    return await matching_service.evaluate_job_match(
        candidate_id=str(current_user.id),
        job_id=data.job_id,
        resume_id=data.resume_id,
    )


@router.post(
    "/compare-explainable",
    response_model=ExplainableMatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Explainably match a parsed resume profile against a job",
)
async def compare_explainable_resume_with_job(
    data: MatchRequest,
    current_user: User = Depends(get_current_user),
):
    """Return a reconciled score, named factor evidence, and recommendation."""
    try:
        return await resume_matching_service.match_resume_to_job(
            candidate_id=str(current_user.id),
            job_id=data.job_id,
            resume_id=data.resume_id,
        )
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.detail) from exc
    except ResumeMatchingError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
