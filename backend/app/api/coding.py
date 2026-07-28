from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user
from app.models.coding import CodingLanguage
from app.models.user import User
from app.schemas.coding import CodingQuestion, CodingSubmissionCreate, CodingSubmissionResponse
from app.services import coding_service

router = APIRouter(prefix="/coding", tags=["Coding Practice"])


@router.get("/questions", response_model=list[CodingQuestion])
async def list_questions(language: CodingLanguage | None = None, current_user: User = Depends(get_current_user)):
    return await coding_service.list_questions(language)


@router.post("/submissions", response_model=CodingSubmissionResponse)
async def submit_code(data: CodingSubmissionCreate, current_user: User = Depends(get_current_user)):
    try:
        return await coding_service.submit(str(current_user.id), data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/submissions", response_model=list[CodingSubmissionResponse])
async def list_submissions(current_user: User = Depends(get_current_user)):
    return await coding_service.list_submissions(str(current_user.id))
