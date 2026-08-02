"""
AuditLog document model — append-only immutable audit trail for recruiter actions,
hiring decisions, status changes, and ethics research operations.

DESIGN & IMMUTABILITY NOTES:
----------------------------
1. Immutability Boundary: Audit log immutability is enforced at the application layer
   (no update/delete HTTP routes or repository methods exist). Direct database access
   or administrative MongoDB commands could still alter records.
2. Type Rationale for `target_resource_id`: `target_resource_id` is typed as `str` (unlike
   `acting_user_id` which is `PydanticObjectId`). This is an intentional design choice to allow
   universal polymorphic referencing across heterogeneous target entity types (e.g. Job ObjectIds,
   Candidate User ObjectIds, Interview Session ObjectIds, or external string keys) without schema
   casting errors.
"""

from datetime import datetime
from typing import Any, Optional
from beanie import Document, PydanticObjectId
from pydantic import Field


class AuditLog(Document):
    """
    Append-only audit log record capturing recruiter decisions, candidate status changes,
    and process bias audit queries.
    """

    acting_user_id: PydanticObjectId = Field(
        ..., description="ObjectId hex string of the authenticated user performing the action"
    )
    acting_user_email: str = Field(..., description="Email address of the acting user")
    acting_user_role: str = Field(..., description="Role of the acting user ('recruiter', 'admin', 'candidate')")
    action_type: str = Field(
        ...,
        description="Type of action performed (e.g., 'hiring_decision', 'bias_audit_query', 'status_change', 'candidate_ranking')",
    )
    target_resource_id: str = Field(
        ...,
        description="Universal string ID of the target resource (Candidate ID, Job ID, Session ID, etc.)",
    )
    target_resource_type: str = Field(
        ...,
        description="Resource entity category ('candidate', 'job', 'application', 'session')",
    )
    decision_reason: Optional[str] = Field(
        default=None, description="Natural language justification or decision reason"
    )
    details: dict[str, Any] = Field(
        default_factory=dict, description="Additional context, scores, or query parameters"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp of when the action occurred"
    )

    class Settings:
        name = "audit_logs"
