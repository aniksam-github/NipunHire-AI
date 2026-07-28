from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.coach import CoachMessageResponse, CoachQuestion
from app.services import coach_service

router = APIRouter(prefix="/career-coach", tags=["AI Career Coach"])


@router.post("/ask", response_model=CoachMessageResponse)
async def ask_coach(data: CoachQuestion, current_user: User = Depends(get_current_user)):
    return await coach_service.ask(str(current_user.id), data)


@router.get("/history", response_model=list[CoachMessageResponse])
async def coach_history(current_user: User = Depends(get_current_user)):
    return await coach_service.history(str(current_user.id))
