"""
Job Repository — database operations for Job documents using Beanie.
"""

from typing import Optional
from beanie import PydanticObjectId

from app.models.job import Job


async def create(job: Job) -> Job:
    """Inserts a new Job document into MongoDB."""
    return await job.insert()


async def get_by_id(job_id: str) -> Optional[Job]:
    """Fetches a Job by ObjectId string."""
    try:
        obj_id = PydanticObjectId(job_id)
        return await Job.get(obj_id)
    except Exception:
        return None


async def list_jobs(
    skip: int = 0,
    limit: int = 20,
    recruiter_id: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> list[Job]:
    """Queries jobs with optional filtering & pagination."""
    query = Job.find()

    if recruiter_id:
        try:
            query = query.find(Job.created_by == PydanticObjectId(recruiter_id))
        except Exception:
            pass

    if is_active is not None:
        query = query.find(Job.is_active == is_active)

    return await query.sort("-created_at").skip(skip).limit(limit).to_list()


async def update(job: Job, update_data: dict) -> Job:
    """Updates fields on an existing Job instance."""
    for key, value in update_data.items():
        if value is not None and hasattr(job, key):
            setattr(job, key, value)
    await job.save()
    return job


async def delete(job: Job) -> None:
    """Deletes a Job document."""
    await job.delete()
                    
