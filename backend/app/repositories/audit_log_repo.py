"""
AuditLog Repository — Append-only data access layer for audit log records.

STRICT DESIGN RULE:
-------------------
This repository contains strictly CREATE and READ methods.
NO update, patch, or delete methods exist in this repository to enforce
application-layer immutability.
"""

from beanie import PydanticObjectId
from app.models.audit_log import AuditLog


async def create(audit_log: AuditLog) -> AuditLog:
    """Create and persist a new append-only audit log entry."""
    await audit_log.insert()
    return audit_log


async def list_by_resource(
    target_resource_id: str, limit: int = 50
) -> list[AuditLog]:
    """Retrieve audit trail logs for a specific target resource ID (candidate, job, application, session)."""
    return (
        await AuditLog.find(AuditLog.target_resource_id == target_resource_id)
        .sort(-AuditLog.timestamp)
        .limit(limit)
        .to_list()
    )


async def list_all(limit: int = 100) -> list[AuditLog]:
    """Retrieve the latest audit trail logs across all system activities."""
    return await AuditLog.find_all().sort(-AuditLog.timestamp).limit(limit).to_list()
