"""
Audit Logs API Router — Read-only endpoints for viewing immutable candidate and job audit trails.
Guarded strictly by recruiter/admin role dependencies.

IMMUTABILITY RULE:
------------------
No POST, PUT, PATCH, or DELETE endpoints exist on this router.
Audit entries are appended automatically by the domain system, never created manually via public API calls.
"""

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import require_role
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse
from app.services import audit_service

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs & Compliance"],
    dependencies=[Depends(require_role("recruiter", "admin"))],
)


@router.get(
    "",
    response_model=list[AuditLogResponse],
    status_code=status.HTTP_200_OK,
    summary="List audit trail history",
    description="Returns the latest audit log entries across recruiter actions and ethics operations.",
)
async def list_all_audit_logs(
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Depends(require_role("recruiter", "admin")),
) -> list[AuditLogResponse]:
    """Retrieve system-wide audit logs for recruiters and admins."""
    logs = await audit_service.get_all_audit_logs(limit=limit)
    return [AuditLogResponse.model_validate(log) for log in logs]


@router.get(
    "/resource/{resource_id}",
    response_model=list[AuditLogResponse],
    status_code=status.HTTP_200_OK,
    summary="View audit history for a candidate or job resource",
    description="Returns audit trail entries filtered by target candidate ID, job ID, or session ID.",
)
async def list_audit_logs_for_resource(
    resource_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(require_role("recruiter", "admin")),
) -> list[AuditLogResponse]:
    """Retrieve audit history for a specific candidate, job, or application ID."""
    logs = await audit_service.get_audit_logs_for_resource(
        target_resource_id=resource_id, limit=limit
    )
    return [AuditLogResponse.model_validate(log) for log in logs]
