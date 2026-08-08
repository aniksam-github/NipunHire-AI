"""
IdempotencyMiddleware — API Idempotency enforcement middleware.

Ensures that repeating identical POST/PUT/PATCH API requests with an `Idempotency-Key` 
header returns the exact cached response without re-executing business logic or AI operations.
"""

import time
import logging
from typing import Dict, Optional, Tuple, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

logger = logging.getLogger(__name__)


class IdempotencyRecord:
    def __init__(self, status_code: int, headers: Dict[str, str], body: bytes, created_at: float):
        self.status_code = status_code
        self.headers = headers
        self.body = body
        self.created_at = created_at


class IdempotencyStore:
    """
    In-memory store for idempotency keys and cached API responses.
    Can be seamlessly extended to Redis for distributed multi-instance deployment.
    """

    def __init__(self, ttl_seconds: int = 86400):
        self.ttl_seconds = ttl_seconds
        # key -> IdempotencyRecord or "PROCESSING"
        self._store: Dict[str, Any] = {}

    def clear(self) -> None:
        """Reset idempotency store (used in unit tests)."""
        self._store.clear()

    def get(self, key: str) -> Optional[Any]:
        self._cleanup()
        return self._store.get(key)

    def set_processing(self, key: str) -> bool:
        """Set state to PROCESSING. Returns False if key already exists."""
        self._cleanup()
        if key in self._store:
            return False
        self._store[key] = "PROCESSING"
        return True

    def set_response(self, key: str, status_code: int, headers: Dict[str, str], body: bytes) -> None:
        """Cache completed response record."""
        # Filter out transport-specific headers
        filtered_headers = {
            k: v for k, v in headers.items()
            if k.lower() not in ("content-length", "content-encoding", "transfer-encoding")
        }
        self._store[key] = IdempotencyRecord(
            status_code=status_code,
            headers=filtered_headers,
            body=body,
            created_at=time.time()
        )

    def remove(self, key: str) -> None:
        """Remove key if request processing fails."""
        self._store.pop(key, None)

    def _cleanup(self) -> None:
        """Remove expired records."""
        now = time.time()
        expired = [
            k for k, v in self._store.items()
            if isinstance(v, IdempotencyRecord) and (now - v.created_at) > self.ttl_seconds
        ]
        for k in expired:
            del self._store[k]


idempotency_store = IdempotencyStore()


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """
    Middleware that inspects `Idempotency-Key` or `X-Idempotency-Key` headers on mutating HTTP requests.
    """

    def __init__(self, app, store: Optional[IdempotencyStore] = None):
        super().__init__(app)
        self.store = store or idempotency_store
        self.supported_methods = {"POST", "PUT", "PATCH"}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method not in self.supported_methods:
            return await call_next(request)

        # Retrieve idempotency key from request headers
        idempotency_key = request.headers.get("Idempotency-Key") or request.headers.get("X-Idempotency-Key")
        if not idempotency_key:
            return await call_next(request)

        idempotency_key = idempotency_key.strip()
        if not idempotency_key:
            return await call_next(request)

        # Check existing record in store
        cached = self.store.get(idempotency_key)

        if cached == "PROCESSING":
            logger.warning(f"Concurrent request with Idempotency-Key '{idempotency_key}' detected.")
            return JSONResponse(
                status_code=409,
                content={"detail": f"A request with Idempotency-Key '{idempotency_key}' is currently being processed."}
            )

        if isinstance(cached, IdempotencyRecord):
            logger.info(f"Replaying cached response for Idempotency-Key '{idempotency_key}'.")
            headers = dict(cached.headers)
            headers["X-Idempotent-Replayed"] = "true"
            return Response(
                content=cached.body,
                status_code=cached.status_code,
                headers=headers,
                media_type=headers.get("content-type", "application/json")
            )

        # Mark key as processing
        if not self.store.set_processing(idempotency_key):
            return JSONResponse(
                status_code=409,
                content={"detail": f"A request with Idempotency-Key '{idempotency_key}' is currently being processed."}
            )

        try:
            response = await call_next(request)

            # Consume response body to cache it
            response_body = [chunk async for chunk in response.body_iterator]
            full_body = b"".join(response_body)

            # Only cache successful/client error responses (exclude 5xx server errors for retry safety)
            if response.status_code < 500:
                headers = dict(response.headers)
                self.store.set_response(
                    key=idempotency_key,
                    status_code=response.status_code,
                    headers=headers,
                    body=full_body
                )
            else:
                self.store.remove(idempotency_key)

            # Return original response content
            return Response(
                content=full_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )

        except Exception:
            self.store.remove(idempotency_key)
            raise
