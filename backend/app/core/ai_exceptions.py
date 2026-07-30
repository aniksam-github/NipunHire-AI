"""Exceptions raised by the reusable AI foundation."""


class AIServiceError(Exception):
    """Base exception for all AI service failures."""


class AIRetryExhaustedError(AIServiceError):
    """Raised when all retry attempts are exhausted."""


class AIResponseValidationError(AIServiceError):
    """Raised when the AI response fails Pydantic validation."""


class AINonRetryableError(AIServiceError):
    """Raised for errors that should never be retried (auth, bad request)."""
