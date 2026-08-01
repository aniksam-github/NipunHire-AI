"""Exceptions raised by the reusable AI foundation."""

from app.core.exceptions import NipunHireException


class AIServiceError(NipunHireException):
    """Base exception for all AI service failures."""

    def __init__(self, detail: str = "AI Service operation failed"):
        super().__init__(detail=detail)


class AIRetryExhaustedError(AIServiceError):
    """Raised when all retry attempts are exhausted."""

    def __init__(self, detail: str = "AI service retry attempts exhausted"):
        super().__init__(detail=detail)


class AIResponseValidationError(AIServiceError):
    """Raised when the AI response fails Pydantic validation."""

    def __init__(self, detail: str = "AI response failed validation"):
        super().__init__(detail=detail)


class AINonRetryableError(AIServiceError):
    """Raised for errors that should never be retried (auth, bad request)."""

    def __init__(self, detail: str = "AI non-retryable error occurred"):
        super().__init__(detail=detail)
