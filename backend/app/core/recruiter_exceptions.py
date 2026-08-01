"""
Recruiter domain exceptions for NipunHire AI.
"""

from app.core.exceptions import NipunHireException


class RecruiterError(NipunHireException):
    """Base exception for recruiter AI operations."""

    def __init__(self, detail: str = "Recruiter operation error occurred"):
        super().__init__(detail=detail)


class RecruiterAuthorizationError(RecruiterError):
    """Raised when non-recruiter users attempt to access recruiter-only endpoints."""

    def __init__(self, detail: str = "Only recruiters and admins can access this resource"):
        super().__init__(detail=detail)


class CandidateSummaryGenerationError(RecruiterError):
    """Raised when generating candidate summary, comparison, or ranking fails."""

    def __init__(self, detail: str = "Failed to generate candidate summary via AI"):
        super().__init__(detail=detail)


class JobDescriptionGenerationError(RecruiterError):
    """Raised when AI job description generation fails."""

    def __init__(self, detail: str = "Failed to generate job description via AI"):
        super().__init__(detail=detail)
