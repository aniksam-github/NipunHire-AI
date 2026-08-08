"""
Unit tests for RateLimiter and RateLimiterMiddleware (Checklist / Improvement #1).
Verifies request tracking, sliding window threshold enforcement, 429 response structure,
and Retry-After header calculation.
"""

import pytest
from fastapi.testclient import TestClient
from app.core.rate_limit import RateLimiter, rate_limiter
from app.main import app


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset the rate limiter state before each test."""
    rate_limiter.clear()
    rate_limiter.enabled = True
    yield
    rate_limiter.clear()


def test_rate_limiter_unit_logic():
    limiter = RateLimiter()
    limiter.clear()

    # Default limit is 100/min, login limit is 5/min
    ip = "192.168.1.100"
    path = "/api/v1/auth/login"

    # First 5 requests should pass
    for _ in range(5):
        is_limited, _ = limiter.is_rate_limited(ip, path)
        assert not is_limited

    # 6th request should be rate limited
    is_limited, retry_after = limiter.is_rate_limited(ip, path)
    assert is_limited
    assert retry_after > 0


def test_rate_limiter_different_ips():
    limiter = RateLimiter()
    limiter.clear()

    ip1 = "10.0.0.1"
    ip2 = "10.0.0.2"
    path = "/api/v1/auth/login"

    # Max out IP 1
    for _ in range(5):
        limiter.is_rate_limited(ip1, path)

    # IP 1 is limited, IP 2 is not
    limited_ip1, _ = limiter.is_rate_limited(ip1, path)
    limited_ip2, _ = limiter.is_rate_limited(ip2, path)

    assert limited_ip1 is True
    assert limited_ip2 is False


def test_rate_limiter_middleware_http_429():
    client = TestClient(app)
    endpoint = "/api/v1/auth/login"

    # Send 5 requests (all should get non-429 response, e.g. 422 for empty body)
    for _ in range(5):
        response = client.post(endpoint, json={"email": "test@domain.com", "password": "wrong"})
        assert response.status_code in (401, 422)

    # 6th request should hit 429 Too Many Requests
    response = client.post(endpoint, json={"email": "test@domain.com", "password": "wrong"})
    assert response.status_code == 429
    data = response.json()
    assert "detail" in data
    assert "Rate limit exceeded" in data["detail"]
    assert "Retry-After" in response.headers
    assert int(response.headers["Retry-After"]) > 0
