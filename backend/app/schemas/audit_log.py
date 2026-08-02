"""
Pydantic schemas for Audit Trail API responses.
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    """Read-only transfer schema for immutable audit log entries."""

    id: str = Field(..., description="Audit log entry ObjectId hex string")
    acting_user_id: str
    acting_user_email: str
    acting_user_role: str
    action_type: str
    target_resource_id: str
    target_resource_type: str
    decision_reason: Optional[str] = None
    details: dict[str, Any]
    timestamp: datetime

    class Config:
        from_attributes = True
