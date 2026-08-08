"""
AI Interview Router — Phase 6 Interview AI simulation, adaptive turns, answer evaluation,
and report generation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.core.exceptions import EntityNotFoundError
from app.core.interview_exceptions import (
    InterviewGenerationError,
    InterviewSessionCompletedError,
    InterviewSessionNotFoundError,
)
from app.models.user import User
from app.schemas.interview import (
    InterviewCreate,
    InterviewReportResponse,
    InterviewResponse,
    InterviewSessionResponse,
    InterviewSessionStartRequest,
    InterviewSessionStartResponse,
    InterviewSubmit,
    InterviewTurnSubmitRequest,
    InterviewTurnSubmitResponse,
)
from app.services import interview_service

router = APIRouter(prefix="/interviews", tags=["AI Interview Simulation & Evaluation"])


# --- Phase 6 Adaptive Interview Endpoints ---

@router.post(
    "/session/start",
    response_model=InterviewSessionStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start an adaptive AI interview session",
)
async def start_adaptive_interview_session(
    data: InterviewSessionStartRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Initializes a new stateful interview session, generating initial questions
    calibrated to candidate profile, target job, and difficulty level.
    """
    try:
        return await interview_service.start_interview_session(str(current_user.id), data)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc
    except InterviewGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post(
    "/session/{session_id}/turn",
    response_model=InterviewTurnSubmitResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit candidate answer for current turn and get adaptive next question",
)
async def submit_adaptive_turn(
    session_id: str,
    data: InterviewTurnSubmitRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Evaluates submitted answer across 5 dimensions, compares with ideal answer,
    adapts difficulty level for the next question, and persists turn state.
    Verifies candidate ownership (returns 404 if unauthorized).
    """
    try:
        return await interview_service.submit_interview_turn(str(current_user.id), session_id, data)
    except InterviewSessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc
    except InterviewSessionCompletedError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.detail) from exc
    except InterviewGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post(
    "/session/{session_id}/complete",
    response_model=InterviewReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete interview session and generate final report",
)
async def complete_interview_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Aggregates per-turn evaluations and produces the final interview report.
    Verifies candidate ownership (returns 404 if unauthorized).
    """
    try:
        return await interview_service.generate_final_report(str(current_user.id), session_id)
    except InterviewSessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc
    except InterviewSessionCompletedError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.detail) from exc
    except InterviewGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post(
    "/session/{session_id}/abandon",
    response_model=InterviewSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Abandon an active interview session",
)
async def abandon_interview_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Explicitly marks an active or incomplete interview session as abandoned.
    Verifies candidate ownership (returns 404 if unauthorized).
    """
    try:
        return await interview_service.abandon_interview_session(str(current_user.id), session_id)
    except InterviewSessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc


@router.get(
    "/session/{session_id}/report",
    response_model=InterviewReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve final interview report",
)
async def get_interview_report(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves the final report generated for a completed interview session.
    Verifies candidate ownership (returns 404 if unauthorized).
    """
    try:
        return await interview_service.generate_final_report(str(current_user.id), session_id)
    except InterviewSessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc
    except InterviewSessionCompletedError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.detail) from exc
    except InterviewGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get(
    "/session/{session_id}",
    response_model=InterviewSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve full interview session state",
)
async def get_interview_session_details(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves current state of an interview session including Q&A turns.
    Verifies candidate ownership (returns 404 if unauthorized).
    """
    try:
        return await interview_service.get_session_details(str(current_user.id), session_id)
    except InterviewSessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc


# --- Legacy Practice Endpoints (Backward Compatibility) ---

@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def start_interview(data: InterviewCreate, current_user: User = Depends(get_current_user)):
    return await interview_service.start_interview(str(current_user.id), data)


@router.get("", response_model=list[InterviewResponse])
async def list_interviews(current_user: User = Depends(get_current_user)):
    return await interview_service.list_interviews(str(current_user.id))


@router.post("/{interview_id}/submit", response_model=InterviewResponse)
async def submit_interview(interview_id: str, data: InterviewSubmit, current_user: User = Depends(get_current_user)):
    try:
        return await interview_service.submit_interview(str(current_user.id), interview_id, data)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc
