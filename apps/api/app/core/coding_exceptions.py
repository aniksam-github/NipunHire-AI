"""
Coding domain exceptions for NipunHire AI.
"""

from app.core.exceptions import NipunHireException


class CodingError(NipunHireException):
    """Base exception for coding AI processing errors."""

    def __init__(self, detail: str = "Coding AI processing error occurred"):
        super().__init__(detail=detail)


class CodingQuestionNotFoundError(CodingError):
    """Raised when a requested coding question is not found."""

    def __init__(self, question_id: str):
        super().__init__(detail=f"Coding question '{question_id}' not found")


class CodingSubmissionNotFoundError(CodingError):
    """Raised when a requested coding submission is not found."""

    def __init__(self, submission_id: str):
        super().__init__(detail=f"Coding submission '{submission_id}' not found")


class CodingReviewGenerationError(CodingError):
    """Raised when AI coding question or review generation fails."""

    def __init__(self, detail: str = "Coding AI generation failed"):
        super().__init__(detail=detail)
