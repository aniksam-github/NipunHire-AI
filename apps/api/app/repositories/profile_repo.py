"""
Profile Repository — database operations for Profile documents using Beanie.
"""

from typing import Optional
from beanie import PydanticObjectId
from app.models.profile import Profile


async def get_by_candidate(candidate_id: str) -> Optional[Profile]:
    """Fetches candidate profile by User ID."""
    try:
        cand_oid = PydanticObjectId(candidate_id)
        return await Profile.find_one(Profile.candidate_id == cand_oid)
    except Exception:
        return None


async def create(profile: Profile) -> Profile:
    """Inserts a new Profile document."""
    return await profile.insert()


async def update(profile: Profile, update_dict: dict) -> Profile:
    """Updates fields on an existing Profile document."""
    for key, value in update_dict.items():
        if value is not None and hasattr(profile, key):
            setattr(profile, key, value)
    await profile.save()
    return profile
