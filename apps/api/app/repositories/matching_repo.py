"""
JobMatch Repository — database operations for JobMatch documents using Beanie.
"""

from typing import Optional
from beanie import PydanticObjectId
from app.models.matching import JobMatch


async def create(match: JobMatch) -> JobMatch:
    """Inserts a new JobMatch document."""
    return await match.insert()


async def get_by_candidate_and_job(candidate_id: str, job_id: str) -> Optional[JobMatch]:
    """Fetches existing match record for candidate & job."""
    try:
        c_oid = PydanticObjectId(candidate_id)
        j_oid = PydanticObjectId(job_id)
        return await JobMatch.find_one(JobMatch.candidate_id == c_oid, JobMatch.job_id == j_oid)
    except Exception:
        return None


async def list_recent_by_candidate(candidate_id: str, limit: int = 5) -> list[JobMatch]:
    """Return recent stored matches to ground career-coach suggestions."""
    try:
        candidate_oid = PydanticObjectId(candidate_id)
        return await JobMatch.find(JobMatch.candidate_id == candidate_oid).sort("-created_at").limit(limit).to_list()
    except Exception:
        return []
