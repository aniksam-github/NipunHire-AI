"""
Application Service — business logic for candidate job application pipeline tracking.
"""

from datetime import datetime, timezone
import logging
from beanie import PydanticObjectId

from app.core.exceptions import EntityNotFoundError, DuplicateEntityError, AuthorizationError
from app.models.application import Application, ApplicationStatus, TimelineEvent
from app.repositories import application_repo, job_repo
from app.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationStatusUpdate
from app.services import notification_service

logger = logging.getLogger(__name__)


def _build_application_response(app: Application) -> ApplicationResponse:
    """Maps Application document to ApplicationResponse."""
    return ApplicationResponse(
        id=str(app.id),
        candidate_id=str(app.candidate_id),
        job_id=str(app.job_id),
        resume_id=str(app.resume_id) if app.resume_id else None,
        status=app.status,
        notes=app.notes,
        timeline=app.timeline,
        created_at=app.created_at,
        updated_at=app.updated_at,
    )


async def apply_for_job(candidate_id: str, data: ApplicationCreate) -> ApplicationResponse:
    """Creates a new job application record in candidate's pipeline."""
    job = await job_repo.get_by_id(data.job_id)
    if not job:
        raise EntityNotFoundError(entity="Job", identifier=data.job_id)

    existing = await application_repo.get_by_candidate_and_job(candidate_id, data.job_id)
    if existing:
        raise DuplicateEntityError(entity="Application", field="job_id")

    cand_oid = PydanticObjectId(candidate_id)
    job_oid = PydanticObjectId(data.job_id)
    res_oid = PydanticObjectId(data.resume_id) if data.resume_id else None

    now = datetime.now(timezone.utc)
    initial_event = TimelineEvent(status=ApplicationStatus.APPLIED, timestamp=now, note="Applied via NipunHire AI Portal")

    app = Application(
        candidate_id=cand_oid,
        job_id=job_oid,
        resume_id=res_oid,
        status=ApplicationStatus.APPLIED,
        notes=data.notes,
        timeline=[initial_event],
    )
    app = await application_repo.create(app)
    await notification_service.create(candidate_id, "Application submitted", f"Your application for {job.title} is now being tracked.", "application")
    logger.info("Candidate %s applied for job %s (Application ID: %s)", candidate_id, data.job_id, str(app.id))
    return _build_application_response(app)


async def list_candidate_applications(candidate_id: str) -> list[ApplicationResponse]:
    """Lists candidate application pipeline items."""
    apps = await application_repo.list_by_candidate(candidate_id)
    return [_build_application_response(a) for a in apps]


async def update_application_status(
    app_id: str,
    data: ApplicationStatusUpdate,
    user_id: str,
) -> ApplicationResponse:
    """Updates status pipeline stage for an application."""
    app = await application_repo.get_by_id(app_id)
    if not app:
        raise EntityNotFoundError(entity="Application", identifier=app_id)

    now = datetime.now(timezone.utc)
    new_event = TimelineEvent(status=data.status, timestamp=now, note=data.note or f"Status changed to {data.status}")

    app.status = data.status
    app.timeline.append(new_event)
    app.updated_at = now

    await app.save()
    logger.info("Application %s status updated to: %s", app_id, data.status)
    return _build_application_response(app)
