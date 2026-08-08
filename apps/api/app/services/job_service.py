"""
Job Service — business logic for job postings.
"""

from datetime import datetime, timezone
import logging
from beanie import PydanticObjectId

from app.core.exceptions import EntityNotFoundError, AuthorizationError
from app.models.job import Job
from app.repositories import job_repo
from app.schemas.job import JobCreate, JobResponse, JobUpdate

logger = logging.getLogger(__name__)


def _build_job_response(job: Job) -> JobResponse:
    """Maps a Job document to a JobResponse schema."""
    return JobResponse(
        id=str(job.id),
        title=job.title,
        description=job.description,
        department=job.department,
        location=job.location,
        employment_type=job.employment_type,
        min_experience_years=job.min_experience_years,
        required_skills=job.required_skills,
        optional_skills=job.optional_skills,
        is_active=job.is_active,
        created_by=str(job.created_by),
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


async def create_job(data: JobCreate, recruiter_id: str) -> JobResponse:
    """Creates a new job posting for a recruiter."""
    job = Job(
        title=data.title,
        description=data.description,
        department=data.department,
        location=data.location,
        employment_type=data.employment_type,
        min_experience_years=data.min_experience_years,
        required_skills=data.required_skills,
        optional_skills=data.optional_skills,
        created_by=PydanticObjectId(recruiter_id),
    )
    job = await job_repo.create(job)
    logger.info("Job created: %s (ID: %s)", job.title, str(job.id))
    return _build_job_response(job)


async def get_job_by_id(job_id: str) -> JobResponse:
    """Fetches job details by ID."""
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise EntityNotFoundError(entity="Job", identifier=job_id)
    return _build_job_response(job)


async def list_jobs(
    skip: int = 0,
    limit: int = 20,
    recruiter_id: str | None = None,
    is_active: bool | None = None,
) -> list[JobResponse]:
    """Lists job postings."""
    jobs = await job_repo.list_jobs(skip=skip, limit=limit, recruiter_id=recruiter_id, is_active=is_active)
    return [_build_job_response(j) for j in jobs]


async def update_job(job_id: str, data: JobUpdate, recruiter_id: str) -> JobResponse:
    """Updates an existing job posting."""
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise EntityNotFoundError(entity="Job", identifier=job_id)

    if str(job.created_by) != recruiter_id:
        raise AuthorizationError(detail="You can only update job postings you created.")

    update_dict = data.model_dump(exclude_unset=True)
    update_dict["updated_at"] = datetime.now(timezone.utc)

    updated_job = await job_repo.update(job, update_dict)
    logger.info("Job updated: %s", job_id)
    return _build_job_response(updated_job)


async def delete_job(job_id: str, recruiter_id: str) -> None:
    """Deletes a job posting."""
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise EntityNotFoundError(entity="Job", identifier=job_id)

    if str(job.created_by) != recruiter_id:
        raise AuthorizationError(detail="You can only delete job postings you created.")

    await job_repo.delete(job)
    logger.info("Job deleted: %s", job_id)
