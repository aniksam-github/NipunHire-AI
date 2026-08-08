"""
Global FastAPI exception handlers for NipunHire AI.

Translates domain exceptions into structured HTTP JSON responses.
"""

import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.ai_exceptions import AIServiceError
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DuplicateEntityError,
    EntityNotFoundError,
    NipunHireException,
)

logger = logging.getLogger(__name__)


async def nipunhire_exception_handler(request: Request, exc: NipunHireException) -> JSONResponse:
    """Global exception handler for all NipunHire domain exceptions."""
    if isinstance(exc, EntityNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, DuplicateEntityError):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, AuthorizationError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, AIServiceError):
        status_code = status.HTTP_502_BAD_GATEWAY
    else:
        status_code = status.HTTP_400_BAD_REQUEST

    logger.warning("Domain exception caught [%s]: %s (path: %s)", status_code, exc.detail, request.url.path)
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.detail},
    )


def register_exception_handlers(app) -> None:
    """Registers exception handlers on the FastAPI application instance."""
    app.add_exception_handler(NipunHireException, nipunhire_exception_handler)
