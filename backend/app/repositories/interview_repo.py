"""
Interview Repository — database operations for InterviewSession documents using Beanie.
"""

from typing import Optional
from beanie import PydanticObjectId

from app.models.interview import InterviewSession


async def create_session(session: InterviewSession) -> InterviewSession:
    """Inserts a new InterviewSession document into MongoDB."""
    return await session.insert()


async def get_session_by_id(session_id: str) -> Optional[InterviewSession]:
    """Fetches an InterviewSession by ObjectId string."""
    try:
        obj_id = PydanticObjectId(session_id)
        return await InterviewSession.get(obj_id)
    except Exception:
        return None


async def get_session_by_id_and_candidate(session_id: str, candidate_id: str) -> Optional[InterviewSession]:
    """Fetches an InterviewSession verifying candidate ownership."""
    try:
        s_oid = PydanticObjectId(session_id)
        c_oid = PydanticObjectId(candidate_id)
        return await InterviewSession.find_one(
            InterviewSession.id == s_oid,
            InterviewSession.candidate_id == c_oid,
        )
    except Exception:
        return None


async def save_session(session: InterviewSession) -> InterviewSession:
    """Saves updates to an existing InterviewSession instance."""
    await session.save()
    return session


async def list_sessions_by_candidate(candidate_id: str, limit: int = 20) -> list[InterviewSession]:
    """Queries interview sessions for a candidate sorted by creation date."""
    try:
        cand_oid = PydanticObjectId(candidate_id)
        return (
            await InterviewSession.find(InterviewSession.candidate_id == cand_oid)
            .sort("-created_at")
            .limit(limit)
            .to_list()
        )
    except Exception:
        return []
