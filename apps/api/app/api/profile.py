"""
Profile API Router — candidate profile endpoints.
"""

from fastapi import APIRouter, Depends, status
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.profile import ProfileResponse, ProfileUpdate
from app.services import profile_service

router = APIRouter(prefix="/profile", tags=["Profile Management"])


@router.get(
    "/me",
    response_model=ProfileResponse,
    summary="Get current candidate profile",
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return await profile_service.get_or_create_profile(candidate_id=str(current_user.id))


@router.put(
    "/me",
    response_model=ProfileResponse,
    summary="Update current candidate profile",
)
async def update_my_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
):
    return await profile_service.update_profile(candidate_id=str(current_user.id), data=data)
