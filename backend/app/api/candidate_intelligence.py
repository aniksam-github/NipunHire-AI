"""Review-only Phase 5 resume and ATS optimization endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.candidate_intelligence_exceptions import CandidateIntelligenceError
from app.core.dependencies import get_current_user
from app.core.exceptions import AuthorizationError, EntityNotFoundError
from app.models.user import User
from app.schemas.candidate_intelligence import (
    ATSOptimizerRequest,
    ATSOptimizerResponse,
    ResumeOptimizerRequest,
    ResumeOptimizerResponse,
)
from app.services import candidate_intelligence_service

router = APIRouter(prefix="/candidate-intelligence", tags=["Candidate Intelligence"])


@router.post("/resume-optimizer", response_model=ResumeOptimizerResponse, status_code=status.HTTP_201_CREATED)
async def optimize_resume(data: ResumeOptimizerRequest, current_user: User = Depends(get_current_user)):
    """Persist review-only resume rewrite suggestions; never update the source resume."""
    try:
        return await candidate_intelligence_service.generate_resume_optimization(data, str(current_user.id))
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.detail) from exc
    except CandidateIntelligenceError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.post("/ats-optimizer", response_model=ATSOptimizerResponse, status_code=status.HTTP_201_CREATED)
async def optimize_ats(data: ATSOptimizerRequest, current_user: User = Depends(get_current_user)):
    """Persist job-grounded ATS suggestions; never update the source resume."""
    try:
        return await candidate_intelligence_service.generate_ats_optimization(data, str(current_user.id))
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.detail) from exc
    except CandidateIntelligenceError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
