"""
Interview domain exceptions for NipunHire AI.
"""

from app.core.exceptions import NipunHireException


class InterviewError(NipunHireException):
    """Base exception for interview processing errors."""

    def __init__(self, detail: str = "Interview processing error occurred"):
        super().__init__(detail=detail)


class InterviewSessionNotFoundError(InterviewError):
    """Raised when a requested interview session is not found."""

    def __init__(self, session_id: str):
        super().__init__(detail=f"Interview session '{session_id}' not found")


class InterviewSessionCompletedError(InterviewError):
    """Raised when attempting to submit turns to an already completed session."""

    def __init__(self, session_id: str):
        super().__init__(detail=f"Interview session '{session_id}' is already completed")


class InterviewGenerationError(InterviewError):
    """Raised when AI interview question, evaluation, or report generation fails."""

    def __init__(self, detail: str = "Interview AI generation failed"):
        super().__init__(detail=detail)
