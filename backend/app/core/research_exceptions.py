"""
Research domain exceptions for NipunHire AI.
"""

from app.core.exceptions import NipunHireException


class ResearchError(NipunHireException):
    """Base exception for research feature operations."""

    def __init__(self, detail: str = "Research module error occurred"):
        super().__init__(detail=detail)


class ExplanationTraceError(ResearchError):
    """Raised when consolidating explanation traces fails."""

    def __init__(self, detail: str = "Failed to compile unified explanation trace"):
        super().__init__(detail=detail)


class BiasAuditError(ResearchError):
    """Raised when statistical process auditing fails."""

    def __init__(self, detail: str = "Failed to perform process-level statistical bias audit"):
        super().__init__(detail=detail)


class AnomalyDetectionError(ResearchError):
    """Raised when resume or interview anomaly detection fails."""

    def __init__(self, detail: str = "Failed to run anomaly detection via AI"):
        super().__init__(detail=detail)
