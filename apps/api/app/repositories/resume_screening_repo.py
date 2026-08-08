"""Persistence operations for Phase 3 resume screening results."""

from beanie import PydanticObjectId

from app.models.resume_screening import ResumeScreening


async def get_by_profile_id(profile_id: str) -> ResumeScreening | None:
    """Return the latest screening record for a structured profile."""
    try:
        return await ResumeScreening.find_one(
            ResumeScreening.profile_id == PydanticObjectId(profile_id)
        )
    except Exception:
        return None


async def create(screening: ResumeScreening) -> ResumeScreening:
    """Insert a new screening record."""
    return await screening.insert()


async def save(screening: ResumeScreening) -> ResumeScreening:
    """Persist refreshed screening stages for an existing profile."""
    await screening.save()
    return screening
