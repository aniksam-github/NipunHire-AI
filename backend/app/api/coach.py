from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user
from app.models.user import User
from app.core.candidate_intelligence_exceptions import CandidateIntelligenceError
from app.core.exceptions import EntityNotFoundError
from app.schemas.candidate_intelligence import CareerCoachAnalysisRequest, CareerCoachAnalysisResponse
from app.schemas.coach import CoachMessageResponse, CoachPlanHistoryResponse, CoachQuestion
from app.services import coach_service

router = APIRouter(prefix="/career-coach", tags=["AI Career Coach"])


@router.post("/ask", response_model=CoachMessageResponse)
async def ask_coach(data: CoachQuestion, current_user: User = Depends(get_current_user)):
    return await coach_service.ask(str(current_user.id), data)


@router.get("/history", response_model=list[CoachMessageResponse])
async def coach_history(current_user: User = Depends(get_current_user)):
    return await coach_service.history(str(current_user.id))


@router.post("/analysis", response_model=CareerCoachAnalysisResponse)
async def generate_career_plan(
    data: CareerCoachAnalysisRequest, current_user: User = Depends(get_current_user)
):
    """Create a persisted AI career plan grounded in existing candidate intelligence."""
    try:
        return await coach_service.generate_plan(str(current_user.id), data)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail) from exc
    except CandidateIntelligenceError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/plan-history", response_model=list[CoachPlanHistoryResponse])
async def career_plan_history(current_user: User = Depends(get_current_user)):
    return await coach_service.plan_history(str(current_user.id))
