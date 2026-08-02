"""
Applications API Router — endpoints for candidate job application pipeline tracking.
Automatically records audit events on application status changes (Task 2).
"""

from fastapi import APIRouter, Depends, status
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationStatusUpdate
from app.services import application_service, audit_service

router = APIRouter(prefix="/applications", tags=["Job Applications"])


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Apply for a job position",
)
async def apply_for_job(
    data: ApplicationCreate,
    current_user: User = Depends(get_current_user),
):
    return await application_service.apply_for_job(candidate_id=str(current_user.id), data=data)


@router.get(
    "",
    response_model=list[ApplicationResponse],
    summary="List candidate application pipeline",
)
async def list_applications(
    current_user: User = Depends(get_current_user),
):
    return await application_service.list_candidate_applications(candidate_id=str(current_user.id))


@router.patch(
    "/{application_id}/status",
    response_model=ApplicationResponse,
    summary="Update application pipeline status",
)
async def update_status(
    application_id: str,
    data: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_user),
):
    res = await application_service.update_application_status(
        app_id=application_id,
        data=data,
        user_id=str(current_user.id),
    )
    await audit_service.record_audit_event(
        acting_user=current_user,
        action_type="candidate_status_change",
        target_resource_id=str(res.candidate_id),
        target_resource_type="candidate",
        decision_reason=f"Application status changed to '{data.status}'",
        details={"application_id": application_id, "new_status": data.status},
    )
    return res
