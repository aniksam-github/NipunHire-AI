"""
Resumes API Router — HTTP endpoints for candidate resume PDF upload, parsing,
ATS scorecard retrieval, and deletion.
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.resume import ResumeResponse
from app.services import resume_service

router = APIRouter(prefix="/resumes", tags=["Resume Center"])

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB limit


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
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF resume files (.pdf) are supported.",
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 5 MB limit.",
        )

    return await resume_service.process_and_save_resume(
        filename=file.filename,
        file_bytes=file_bytes,
        candidate_id=str(current_user.id),
    )


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
