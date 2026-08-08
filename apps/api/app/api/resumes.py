"""
Resumes API Router — HTTP endpoints for candidate resume PDF upload, parsing,
ATS scorecard retrieval, inline editing/correction, and deletion.
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status

from app.core.dependencies import get_current_user
from app.core.exceptions import AuthorizationError, EntityNotFoundError
from app.core.resume_exceptions import (
    ResumeExtractionError,
    ResumeParsingError,
    ResumeSummaryError,
    ResumeUploadError,
)
from app.core.screening_exceptions import ResumeScreeningError
from app.models.user import User
from app.schemas.resume import ResumeResponse, ResumeUpdateRequest
from app.services import resume_service
from app.services import resume_screening_service
from app.schemas.resume_screening import ResumeScreeningResponse

router = APIRouter(prefix="/resumes", tags=["Resume Center"])

@router.post(
    "/upload",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload & Parse PDF Resume",
)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Uploads a candidate PDF resume file, extracts text via PyMuPDF, parses skills & contact info,
    calculates ATS health score, and stores the resume analysis.
    """
    file_bytes = await file.read()
    try:
        return await resume_service.process_and_save_resume(
            filename=file.filename or "",
            content_type=file.content_type,
            file_bytes=file_bytes,
            candidate_id=str(current_user.id),
        )
    except ResumeUploadError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ResumeExtractionError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except (ResumeParsingError, ResumeSummaryError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post(
    "/{resume_id}/screen",
    response_model=ResumeScreeningResponse,
    summary="Analyze an already-parsed resume profile",
)
async def screen_resume(resume_id: str, current_user: User = Depends(get_current_user)):
    """Run Phase 3 analysis, categorized skill extraction, and improvements."""
    try:
        return await resume_screening_service.screen_resume(resume_id, str(current_user.id))
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.detail) from exc
    except ResumeScreeningError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get(
    "",
    response_model=list[ResumeResponse],
    summary="List candidate's uploaded resumes",
)
async def list_resumes(
    current_user: User = Depends(get_current_user),
):
    """
    Returns all resume versions uploaded by the current user.
    """
    return await resume_service.list_candidate_resumes(candidate_id=str(current_user.id))


@router.get(
    "/{resume_id}",
    response_model=ResumeResponse,
    summary="Get detailed ATS Resume Health Scorecard",
)
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves full parsed attributes, ATS score, and AI quality feedback for a specific resume.
    """
    return await resume_service.get_resume_by_id(resume_id=resume_id, candidate_id=str(current_user.id))


@router.patch(
    "/{resume_id}",
    response_model=ResumeResponse,
    summary="Persist candidate AI corrections to parsed email, phone, or extracted skills",
)
async def update_resume_parsed_data(
    resume_id: str,
    payload: ResumeUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Updates and persists human corrections for parsed email, phone, or extracted skills (Checklist #5).
    """
    try:
        return await resume_service.update_resume_parsed_data(
            resume_id=resume_id, candidate_id=str(current_user.id), payload=payload
        )
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.detail) from exc


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete uploaded resume",
)
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Deletes an uploaded resume document and file.
    """
    await resume_service.delete_resume(resume_id=resume_id, candidate_id=str(current_user.id))


@router.get(
    "/profiles/{profile_id}/similar",
    summary="Get semantically similar candidate profiles",
)
async def get_similar_candidate_profiles(
    profile_id: str,
    top_k: int = 5,
    current_user: User = Depends(get_current_user),
):
    """
    Returns candidate profiles with the most semantically similar resume embeddings.
    """
    from app.services.vector_search_service import vector_search_service

    return vector_search_service.search_similar_candidates_for_profile(
        target_profile_id=profile_id, top_k=top_k
    )
