"""Stage-specific failures for the resume intelligence pipeline."""


class ResumePipelineError(Exception):
    """Base failure for resume upload and intelligence processing."""


class ResumeUploadError(ResumePipelineError):
    """Raised when a resume upload is invalid or cannot be stored."""


class ResumeExtractionError(ResumePipelineError):
    """Raised when text cannot be extracted from a PDF resume."""


class ResumeParsingError(ResumePipelineError):
    """Raised when AI parsing of an extracted resume fails."""


class ResumeSummaryError(ResumePipelineError):
    """Raised when AI summary generation for a parsed resume fails."""
