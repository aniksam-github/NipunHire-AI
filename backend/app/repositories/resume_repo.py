"""
Resume Repository — database operations for Resume documents using Beanie.
"""

from typing import Optional
from beanie import PydanticObjectId

from app.models.resume import Resume


async def create(resume: Resume) -> Resume:
    """Inserts a new Resume document into MongoDB."""
    return await resume.insert()


async def get_by_id(resume_id: str) -> Optional[Resume]:
    """Fetches a Resume by ObjectId hex string."""
    try:
        obj_id = PydanticObjectId(resume_id)
        return await Resume.get(obj_id)
    except Exception:
        return None


async def list_by_candidate(candidate_id: str) -> list[Resume]:
    """Lists all uploaded resumes for a candidate sorted by recency."""
    try:
        cand_oid = PydanticObjectId(candidate_id)
        return await Resume.find(Resume.candidate_id == cand_oid).sort("-created_at").to_list()
    except Exception:
        return []


async def delete(resume: Resume) -> None:
    """Deletes a Resume document."""
    await resume.delete()
