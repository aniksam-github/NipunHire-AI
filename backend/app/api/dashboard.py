"""Candidate dashboard API."""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.dashboard import CandidateDashboardResponse
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/me", response_model=CandidateDashboardResponse)
async def get_my_dashboard(
    current_user: User = Depends(get_current_user),
):
    """Return live dashboard metrics for the authenticated candidate."""
    return await dashboard_service.get_candidate_dashboard(str(current_user.id))
