"""
Application Repository — database operations for Application pipeline documents.
"""

from typing import Optional
from beanie import PydanticObjectId
from app.models.application import Application, ApplicationStatus


async def create(app: Application) -> Application:
    """Inserts a new Application document."""
    return await app.insert()


async def get_by_id(app_id: str) -> Optional[Application]:
    """Fetches application by ID."""
    try:
        a_oid = PydanticObjectId(app_id)
        return await Application.get(a_oid)
    except Exception:
        return None


async def get_by_candidate_and_job(candidate_id: str, job_id: str) -> Optional[Application]:
    """Fetches application record for candidate & job."""
    try:
        c_oid = PydanticObjectId(candidate_id)
        j_oid = PydanticObjectId(job_id)
        return await Application.find_one(Application.candidate_id == c_oid, Application.job_id == j_oid)
    except Exception:
        return None


async def list_by_candidate(candidate_id: str) -> list[Application]:
    """Lists candidate applications sorted by update time."""
    try:
        c_oid = PydanticObjectId(candidate_id)
        return await Application.find(Application.candidate_id == c_oid).sort("-updated_at").to_list()
    except Exception:
        return []


async def update(app: Application, update_dict: dict) -> Application:
    """Updates fields on Application document."""
    for key, value in update_dict.items():
        if value is not None and hasattr(app, key):
            setattr(app, key, value)
    await app.save()
    return app
