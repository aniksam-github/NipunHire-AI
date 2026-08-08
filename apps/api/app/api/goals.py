from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.goal import CareerProgressResponse, GoalCreate, GoalProgressUpdate, GoalResponse
from app.services import goal_service

router = APIRouter(tags=["Goals & Progress"])


@router.post("/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(data: GoalCreate, current_user: User = Depends(get_current_user)):
    return await goal_service.create_goal(str(current_user.id), data)


@router.get("/goals", response_model=list[GoalResponse])
async def list_goals(current_user: User = Depends(get_current_user)):
    return await goal_service.list_goals(str(current_user.id))


@router.patch("/goals/{goal_id}/progress", response_model=GoalResponse)
async def update_goal_progress(goal_id: str, data: GoalProgressUpdate, current_user: User = Depends(get_current_user)):
    return await goal_service.update_goal_progress(str(current_user.id), goal_id, data)


@router.get("/progress/me", response_model=CareerProgressResponse)
async def get_progress(current_user: User = Depends(get_current_user)):
    return await goal_service.get_progress(str(current_user.id))
