from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.interview import InterviewCreate, InterviewResponse, InterviewSubmit
from app.services import interview_service

router = APIRouter(prefix="/interviews", tags=["AI Interview Practice"])


@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def start_interview(data: InterviewCreate, current_user: User = Depends(get_current_user)):
    return await interview_service.start_interview(str(current_user.id), data)


@router.get("", response_model=list[InterviewResponse])
async def list_interviews(current_user: User = Depends(get_current_user)):
    return await interview_service.list_interviews(str(current_user.id))


@router.post("/{interview_id}/submit", response_model=InterviewResponse)
async def submit_interview(interview_id: str, data: InterviewSubmit, current_user: User = Depends(get_current_user)):
    return await interview_service.submit_interview(str(current_user.id), interview_id, data)
