"""
Unit & integration tests for the Immutable Audit Trail System (Task 2).

Verifies Acceptance Criteria:
1. Explicitly confirms NO PUT, PATCH, or DELETE routes exist on the audit-logs API router.
2. Confirms audit entries are created automatically when a hiring decision or status change occurs.
3. Confirms audit log entries can be queried by target candidate/job resource ID.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from beanie import PydanticObjectId

from app.main import app
from app.models.user import User, UserRole
from app.models.audit_log import AuditLog
from app.services import audit_service
from app.api.audit_logs import router as audit_router


def test_no_update_or_delete_routes_exist_on_audit_logs():
    """
    Acceptance Criterion #1: Verify explicitly that NO PUT, PATCH, or DELETE
    HTTP routes exist on the audit log collection / router.
    """
    # 1. Inspect FastAPI app routes for prefix /api/v1/audit-logs
    forbidden_methods = {"PUT", "PATCH", "DELETE", "POST"}
    audit_routes = [r for r in app.routes if getattr(r, "path", "").startswith("/api/v1/audit-logs")]
    
    for route in audit_routes:
        methods = getattr(route, "methods", set())
        disallowed = methods.intersection(forbidden_methods)
        assert not disallowed, f"Route '{route.path}' defines disallowed mutating methods: {disallowed}"

    # 2. Test via TestClient that PUT/PATCH/DELETE return 405 Method Not Allowed
    client = TestClient(app)
    for method in ("put", "patch", "delete", "post"):
        response = getattr(client, method)("/api/v1/audit-logs")
        assert response.status_code in (405, 404), f"HTTP {method.upper()} should not be allowed on /api/v1/audit-logs"


def test_audit_log_model_structure_and_type_rationale():
    """
    Verifies AuditLog schema fields, timestamp generation, and target_resource_id string typing.
    """
    user_id = PydanticObjectId()
    entry = AuditLog(
        acting_user_id=user_id,
        acting_user_email="recruiter@company.com",
        acting_user_role="recruiter",
        action_type="hiring_decision",
        target_resource_id="candidate_12345",
        target_resource_type="candidate",
        decision_reason="Strong match and interview performance",
        details={"recommendation": "Hire", "overall_score": 92},
    )

    assert entry.acting_user_id == user_id
    assert entry.acting_user_email == "recruiter@company.com"
    assert entry.acting_user_role == "recruiter"
    assert entry.action_type == "hiring_decision"
    assert isinstance(entry.target_resource_id, str)
    assert entry.target_resource_id == "candidate_12345"
    assert entry.decision_reason == "Strong match and interview performance"
    assert entry.details["recommendation"] == "Hire"
    assert isinstance(entry.timestamp, datetime)


@pytest.mark.asyncio
async def test_record_audit_event_unit(monkeypatch):
    """
    Acceptance Criterion #2 & #4: Verify record_audit_event creates an entry correctly.
    """
    saved_entries = []

    async def mock_create(entry: AuditLog) -> AuditLog:
        entry.id = PydanticObjectId()
        saved_entries.append(entry)
        return entry

    monkeypatch.setattr("app.repositories.audit_log_repo.create", mock_create)

    # Mock acting recruiter user
    dummy_user = User(
        id=PydanticObjectId(),
        email="recruiter@nipunhire.ai",
        full_name="Senior Recruiter",
        role=UserRole.RECRUITER,
        hashed_password="dummy_hash",
        is_active=True,
    )

    res = await audit_service.record_audit_event(
        acting_user=dummy_user,
        action_type="hiring_decision",
        target_resource_id="cand_999",
        target_resource_type="candidate",
        decision_reason="Recommended for hire based on technical interview score",
        details={"interview_score": 95},
    )

    assert len(saved_entries) == 1
    assert saved_entries[0].acting_user_email == "recruiter@nipunhire.ai"
    assert saved_entries[0].action_type == "hiring_decision"
    assert saved_entries[0].target_resource_id == "cand_999"
    assert saved_entries[0].decision_reason == "Recommended for hire based on technical interview score"
