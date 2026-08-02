"""
Audit Trail Service — Domain orchestration for recording and querying append-only audit events.
"""

import logging
from typing import Any, Optional
from beanie import PydanticObjectId
from app.models.audit_log import AuditLog
from app.models.user import User
from app.repositories import audit_log_repo

logger = logging.getLogger(__name__)


async def record_audit_event(
    acting_user: User,
    action_type: str,
    target_resource_id: str,
    target_resource_type: str,
    decision_reason: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
) -> AuditLog:
    """
    Creates and records an immutable audit log entry for recruiter decisions,
    status changes, or bias audit operations.
    """
    audit_entry = AuditLog(
        acting_user_id=acting_user.id,
        acting_user_email=acting_user.email,
        acting_user_role=acting_user.role.value if hasattr(acting_user.role, "value") else str(acting_user.role),
        action_type=action_type,
        target_resource_id=str(target_resource_id),
        target_resource_type=target_resource_type,
        decision_reason=decision_reason,
        details=details or {},
    )
    saved_entry = await audit_log_repo.create(audit_entry)
    logger.info(
        "Recorded audit event '%s' by user %s on resource %s",
        action_type,
        acting_user.email,
        target_resource_id,
    )
    return saved_entry


async def get_audit_logs_for_resource(
    target_resource_id: str, limit: int = 50
) -> list[AuditLog]:
    """Retrieve audit trail logs for a specific candidate or job resource ID."""
    return await audit_log_repo.list_by_resource(target_resource_id=target_resource_id, limit=limit)


async def get_all_audit_logs(limit: int = 100) -> list[AuditLog]:
    """Retrieve system-wide audit trail logs."""
    return await audit_log_repo.list_all(limit=limit)
