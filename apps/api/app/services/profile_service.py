"""
Profile Service — business logic for candidate profile management & completion score.
"""

from datetime import datetime, timezone
import logging
from beanie import PydanticObjectId

from app.core.exceptions import EntityNotFoundError
from app.models.profile import Profile
from app.repositories import profile_repo
from app.schemas.profile import ProfileResponse, ProfileUpdate

logger = logging.getLogger(__name__)


def _calculate_completion_percentage(p: Profile) -> int:
    """Calculates profile completion percentage (0 - 100%)."""
    score = 10  # Base account created
    if p.headline:
        score += 15
    if p.bio:
        score += 15
    if p.education:
        score += 15
    if p.experience:
        score += 15
    if p.projects:
        score += 15
    if p.skills:
        score += 15
    if p.certifications or p.languages:
        score += 5
    if p.github_username or p.linkedin_url or p.portfolio_url:
        score += 5
    return min(100, score)


def _build_profile_response(p: Profile) -> ProfileResponse:
    """Maps a Profile document to ProfileResponse."""
    return ProfileResponse(
        id=str(p.id),
        candidate_id=str(p.candidate_id),
        headline=p.headline,
        bio=p.bio,
        education=p.education,
        experience=p.experience,
        projects=p.projects,
        skills=p.skills,
        certifications=p.certifications,
        languages=p.languages,
        achievements=p.achievements,
        github_username=p.github_username,
        linkedin_url=p.linkedin_url,
        portfolio_url=p.portfolio_url,
        is_public=p.is_public,
        completion_percentage=p.completion_percentage,
    )


async def get_or_create_profile(candidate_id: str) -> ProfileResponse:
    """Gets candidate profile or initializes empty default profile."""
    profile = await profile_repo.get_by_candidate(candidate_id)
    if not profile:
        profile = Profile(
            candidate_id=PydanticObjectId(candidate_id),
            skills=["Python", "FastAPI", "React", "TypeScript", "MongoDB"],
        )
        profile.completion_percentage = _calculate_completion_percentage(profile)
        profile = await profile_repo.create(profile)
        logger.info("Initialized default profile for candidate: %s", candidate_id)

    return _build_profile_response(profile)


async def update_profile(candidate_id: str, data: ProfileUpdate) -> ProfileResponse:
    """Updates candidate profile attributes."""
    profile = await profile_repo.get_by_candidate(candidate_id)
    if not profile:
        profile = Profile(candidate_id=PydanticObjectId(candidate_id))
        profile = await profile_repo.create(profile)

    update_dict = data.model_dump(exclude_unset=True)
    update_dict["updated_at"] = datetime.now(timezone.utc)

    profile = await profile_repo.update(profile, update_dict)
    profile.completion_percentage = _calculate_completion_percentage(profile)
    await profile.save()

    logger.info("Profile updated for candidate: %s (%d%% complete)", candidate_id, profile.completion_percentage)
    return _build_profile_response(profile)
