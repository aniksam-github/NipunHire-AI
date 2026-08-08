"""Persistence operations for structured resume profiles."""

from beanie import PydanticObjectId

from app.models.resume_profile import ResumeProfile


async def create(profile: ResumeProfile) -> ResumeProfile:
    """Persist a profile produced by resume parsing."""
    return await profile.insert()


async def save(profile: ResumeProfile) -> ResumeProfile:
    """Persist later pipeline-stage updates to a profile."""
    await profile.save()
    return profile


async def get_by_resume_id(resume_id: str) -> ResumeProfile | None:
    """Find the structured profile linked to one uploaded resume."""
    try:
        return await ResumeProfile.find_one(
            ResumeProfile.resume_id == PydanticObjectId(resume_id)
        )
    except Exception:
        return None
