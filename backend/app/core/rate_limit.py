"""
RateLimiterMiddleware — Request rate limiting and brute-force protection middleware.
Protects auth endpoints and expensive AI pipelines against abuse, credential brute-forcing,
and API quota exhaustion.

IMPORTANT PRODUCTION LIMITATION NOTE:
-------------------------------------
The current `RateLimiter` implementation uses process-local in-memory state (`self._history`).
Because request timestamps are stored in memory per Python process:
  - Limits will NOT be synchronized across multiple worker processes (e.g., `uvicorn main:app --workers 4`).
  - Limits will NOT be synchronized across multiple container replicas in Kubernetes / cloud clusters.
  - A client could potentially make N * max_requests if requests are round-robined across N workers.

For production multi-worker or multi-node deployments, upgrade `RateLimiter` to a distributed
storage backend (e.g., Redis using `redis-py` or `limits` library with token bucket algorithm).
"""

import time
from collections import defaultdict
import logging
from typing import Dict, List, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Sliding-window rate limiter tracking requests per IP address in process memory.

    Note: In-memory state is local to this worker process. In multi-process production environments,
    use a Redis-backed rate limiter so rate state is shared across worker processes.
    """

    def __init__(self):
        # Maps (client_ip, path_prefix) -> list of timestamp floats
        self._history: Dict[Tuple[str, str], List[float]] = defaultdict(list)
        # Custom limits per path prefix (path_prefix -> (max_requests, window_seconds))
        self._limits: Dict[str, Tuple[int, int]] = {
            "/api/v1/auth/login": (5, 60),
            "/api/v1/auth/register": (5, 60),
            "/api/v1/resumes/upload": (10, 60),
            "/api/v1/interviews": (20, 60),
            "/api/v1/recruiter": (20, 60),
        }
        self.default_limit: Tuple[int, int] = (100, 60)
        self.enabled: bool = True

    def clear(self) -> None:
        """Reset all rate limit histories (used in unit tests)."""
        self._history.clear()

    def get_limit_for_path(self, path: str) -> Tuple[int, int]:
        for prefix, limit in self._limits.items():
            if path.startswith(prefix):
                return limit
        return self.default_limit

    def is_rate_limited(self, ip: str, path: str) -> Tuple[bool, int]:
        if not self.enabled:
            return False, 0

        now = time.time()
        max_requests, window_seconds = self.get_limit_for_path(path)
        key = (ip, path)

        # Remove timestamps outside the sliding window
        window_start = now - window_seconds
        self._history[key] = [t for t in self._history[key] if t > window_start]

        if len(self._history[key]) >= max_requests:
            oldest_timestamp = self._history[key][0]
            retry_after = int(window_seconds - (now - oldest_timestamp)) + 1
            return True, max(1, retry_after)

        self._history[key].append(now)
        return False, 0


# Global singleton instance
rate_limiter = RateLimiter()


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """FastAPI/Starlette middleware enforcing rate limits."""

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "127.0.0.1"
        path = request.url.path

        # Bypass rate limits for OpenAPI docs and healthcheck
        if path in ("/", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        is_limited, retry_after = rate_limiter.is_rate_limited(client_ip, path)
        if is_limited:
            logger.warning("Rate limit exceeded for IP %s on path %s", client_ip, path)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded. Please wait {retry_after} seconds before retrying.",
                    "retry_after_seconds": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
