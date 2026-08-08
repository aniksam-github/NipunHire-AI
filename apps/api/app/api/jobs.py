"""
Jobs API Router — HTTP endpoints for Job position CRUD operations.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.services import job_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job posting",
)
async def create_job(
    data: JobCreate,
    current_user: User = Depends(require_role(UserRole.RECRUITER, UserRole.ADMIN)),
):
    """
    Creates a new job position posting. Requires Recruiter or Admin role.
    """
    return await job_service.create_job(data, recruiter_id=str(current_user.id))


@router.get(
    "",
    response_model=list[JobResponse],
    summary="List all job postings",
)
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    recruiter_only: bool = Query(False, description="If True, filters to jobs created by caller"),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """
    Lists job postings with optional pagination & filters.
    """
    recruiter_id = str(current_user.id) if recruiter_only else None
    return await job_service.list_jobs(
        skip=skip,
        limit=limit,
        recruiter_id=recruiter_id,
        is_active=is_active,
    )


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get job posting details",
)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves details for a specific job position by ID.
    """
    return await job_service.get_job_by_id(job_id)


@router.patch(
    "/{job_id}",
    response_model=JobResponse,
    summary="Update a job posting",
)
async def update_job(
    job_id: str,
    data: JobUpdate,
    current_user: User = Depends(require_role(UserRole.RECRUITER, UserRole.ADMIN)),
):
    """
    Updates an existing job position posting. Only the job creator or Admin can update.
    """
    return await job_service.update_job(job_id, data, recruiter_id=str(current_user.id))


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a job posting",
)
async def delete_job(
    job_id: str,
    current_user: User = Depends(require_role(UserRole.RECRUITER, UserRole.ADMIN)),
):
    """
    Deletes a job position posting. Only the job creator or Admin can delete.
    """
    await job_service.delete_job(job_id, recruiter_id=str(current_user.id))
