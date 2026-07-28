"""
Matching API Router — job description vs resume matching & skill gap analysis endpoints.
"""

from fastapi import APIRouter, Depends, status
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.matching import MatchRequest, MatchResponse
from app.services import matching_service

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
