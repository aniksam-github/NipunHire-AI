"""
Unit & integration tests for IdempotencyStore and IdempotencyMiddleware.
Verifies header detection, response caching, replaying cached responses,
and duplicate request prevention.
"""

import pytest
from fastapi.testclient import TestClient
from app.core.idempotency import idempotency_store
from app.main import app


@pytest.fixture(autouse=True)
def reset_idempotency_store():
    """Reset the idempotency store before each test."""
    idempotency_store.clear()
    yield
    idempotency_store.clear()


def test_idempotency_store_unit_logic():
    idempotency_store.clear()
    key = "test-uuid-12345"

    assert idempotency_store.get(key) is None
    assert idempotency_store.set_processing(key) is True
    # Second processing lock attempt should fail
    assert idempotency_store.set_processing(key) is False

    idempotency_store.set_response(key, 200, {"content-type": "application/json"}, b'{"ok": true}')
    record = idempotency_store.get(key)
    assert record is not None
    assert record.status_code == 200
    assert record.body == b'{"ok": true}'


def test_idempotency_middleware_replay():
    client = TestClient(app)
    endpoint = "/health"
    key = "test-idempotency-key-001"

    # GET request with key should not use idempotency cache
    get_res = client.get(endpoint, headers={"Idempotency-Key": key})
    assert get_res.status_code == 200
    assert "X-Idempotent-Replayed" not in get_res.headers

    # Root endpoint GET
    root_res = client.get("/", headers={"Idempotency-Key": key})
    assert root_res.status_code == 200
    assert "X-Idempotent-Replayed" not in root_res.headers


def test_idempotency_post_request_replay():
    client = TestClient(app)
    endpoint = "/api/v1/auth/login"
    key = "test-post-idempotency-key-777"

    headers = {"Idempotency-Key": key}
    payload = {"email": "invalid@domain.com", "password": "wrongpassword"}

    # First request: fails authentication with 401/422
    response1 = client.post(endpoint, json=payload, headers=headers)
    status1 = response1.status_code
    body1 = response1.json()
    assert "X-Idempotent-Replayed" not in response1.headers

    # Second request with SAME Idempotency-Key: returns replayed response
    response2 = client.post(endpoint, json=payload, headers=headers)
    assert response2.status_code == status1
    assert response2.json() == body1
    assert response2.headers.get("X-Idempotent-Replayed") == "true"
