"""
Coding Router — Phase 7 Coding AI endpoints for question generation, static AI review,
code submission, and consolidated feedback.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.core.exceptions import EntityNotFoundError
from app.core.coding_exceptions import (
    CodingQuestionNotFoundError,
    CodingReviewGenerationError,
    CodingSubmissionNotFoundError,
)
from app.models.coding import CodingLanguage
from app.models.user import User
from app.schemas.coding import (
    CodingQuestion,
    CodingQuestionGenerateRequest,
    CodingQuestionGenerateResponse,
    CodingSubmissionCreate,
    CodingSubmissionResponse,
    ConsolidatedCodingFeedbackResponse,
)
from app.services import coding_service

router = APIRouter(prefix="/coding", tags=["Coding AI & Code Review"])


# --- Phase 7 Coding AI Endpoints ---

@router.post(
    "/questions/generate",
    response_model=CodingQuestionGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate an AI-crafted coding challenge for a job context",
)
async def generate_coding_question(
    data: CodingQuestionGenerateRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Generates a coding challenge tailored to target job skills and requested difficulty.
    """
    try:
        return await coding_service.generate_coding_question(str(current_user.id), data)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc
    except CodingReviewGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post(
    "/submissions/review",
    response_model=ConsolidatedCodingFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit candidate code for static AI review",
)
async def submit_code_for_review(
    data: CodingSubmissionCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Accepts candidate code submission, performs static AI code review (correctness,
    bugs/edge cases, time/space complexity analysis, style observations, optimization),
    persists state in DB, and returns consolidated feedback.
    """
    try:
        return await coding_service.submit_candidate_code(str(current_user.id), data)
    except CodingQuestionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc
    except CodingReviewGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get(
    "/submissions/{submission_id}",
    response_model=ConsolidatedCodingFeedbackResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve consolidated question, candidate submission, and AI review",
)
async def get_consolidated_coding_feedback(
    submission_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Returns question, candidate submission, and AI review together in a single view.
    Verifies candidate ownership (returns 404 if unauthorized).
    """
    try:
        return await coding_service.get_consolidated_feedback(str(current_user.id), submission_id)
    except CodingSubmissionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc


# --- Legacy Practice Endpoints (Backward Compatibility) ---

@router.get("/questions", response_model=list[CodingQuestion])
async def list_questions(language: CodingLanguage | None = None, current_user: User = Depends(get_current_user)):
    return await coding_service.list_questions(language)


@router.post("/submissions", response_model=ConsolidatedCodingFeedbackResponse)
async def submit_code_legacy(data: CodingSubmissionCreate, current_user: User = Depends(get_current_user)):
    try:
        return await coding_service.submit_candidate_code(str(current_user.id), data)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/submissions", response_model=list[CodingSubmissionResponse])
async def list_submissions(current_user: User = Depends(get_current_user)):
    return await coding_service.list_submissions(str(current_user.id))
