"""Upload-to-profile orchestration for the resume intelligence pipeline."""

import json
import logging
from pathlib import Path
from uuid import uuid4

from beanie import PydanticObjectId

from app.ai.services.ai_service import AIService
from app.ai.utils.token_utils import estimate_token_count
from app.core.config import BACKEND_DIR, settings
from app.core.exceptions import AuthorizationError, EntityNotFoundError
from app.core.resume_exceptions import (
    ResumeExtractionError,
    ResumeParsingError,
    ResumePipelineError,
    ResumeSummaryError,
    ResumeUploadError,
)
from app.models.resume import Resume
from app.models.resume_profile import ResumeProfile
from app.repositories import resume_profile_repo, resume_repo
from app.schemas.resume import AIFeedbackSchema, QualityBreakdownSchema, ResumeResponse, ResumeUpdateRequest
from app.schemas.resume_intelligence import ResumeParsingResult, ResumeSummaryResult
from app.services import notification_service, pdf_service
from app.services.prompt_service import load_prompt

logger = logging.getLogger(__name__)

MAX_RESUME_FILE_SIZE_BYTES = 5 * 1024 * 1024
# ponytail: local disk is suitable only for single-instance development; move to S3/object storage before scaling.
UPLOAD_DIR = BACKEND_DIR / "uploads" / "resumes"
_PDF_CONTENT_TYPES = {"application/pdf", "application/x-pdf"}


def validate_resume_upload(filename: str | None, content_type: str | None, file_bytes: bytes) -> None:
    """Validate the upload boundary before storing an untrusted file."""
    if not filename or Path(filename).suffix.lower() != ".pdf":
        raise ResumeUploadError("Only PDF resume files (.pdf) are supported.")
    if content_type not in _PDF_CONTENT_TYPES or not file_bytes.startswith(b"%PDF-"):
        raise ResumeUploadError("Uploaded file is not a valid PDF.")
    if len(file_bytes) > MAX_RESUME_FILE_SIZE_BYTES:
        raise ResumeUploadError("Resume file exceeds the 5 MB limit.")


def extract_resume_text(file_bytes: bytes) -> tuple[str, int]:
    """Extract machine-readable resume text independently from AI parsing."""
    try:
        return pdf_service.extract_text_from_pdf_bytes(file_bytes)
    except pdf_service.PDFExtractionError as exc:
        raise ResumeExtractionError(str(exc)) from exc


async def parse_resume_text(raw_text: str, ai_service: AIService) -> ResumeParsingResult:
    """Turn extracted resume text into the validated parser contract."""
    prompt = load_prompt("resume_parsing", resume_text=raw_text)
    logger.info(
        "Prepared AI resume parsing request",
        extra={"stage": "parsing", "estimated_prompt_tokens": estimate_token_count(prompt, settings.OPENAI_MODEL)},
    )
    try:
        return await ai_service.get_structured_response(
            system_prompt="",
            user_prompt=prompt,
            response_model=ResumeParsingResult,
        )
    except Exception as exc:
        raise ResumeParsingError("AI resume parsing failed") from exc


async def generate_resume_summary(
    parsed_profile: ResumeParsingResult, ai_service: AIService
) -> ResumeSummaryResult:
    """Summarize validated structured data, never the raw resume text."""
    profile_json = json.dumps(parsed_profile.model_dump(mode="json"))
    prompt = load_prompt("resume_summary", profile_json=profile_json)
    logger.info(
        "Prepared AI resume summary request",
        extra={"stage": "summary", "estimated_prompt_tokens": estimate_token_count(prompt, settings.OPENAI_MODEL)},
    )
    try:
        return await ai_service.get_structured_response(
            system_prompt="",
            user_prompt=prompt,
            response_model=ResumeSummaryResult,
        )
    except Exception as exc:
        raise ResumeSummaryError("AI resume summary generation failed") from exc


def _build_resume_response(resume: Resume) -> ResumeResponse:
    return ResumeResponse(
        id=str(resume.id),
        candidate_id=str(resume.candidate_id),
        filename=resume.filename,
        file_size_bytes=resume.file_size_bytes,
        page_count=resume.page_count,
        parsed_name=resume.parsed_name,
        parsed_email=resume.parsed_email,
        parsed_phone=resume.parsed_phone,
        extracted_skills=resume.extracted_skills,
        ats_score=resume.ats_score,
        quality_breakdown=QualityBreakdownSchema(**resume.quality_breakdown),
        ai_feedback=AIFeedbackSchema(**resume.ai_feedback),
        is_primary=resume.is_primary,
        created_at=resume.created_at,
    )


async def _mark_failed(resume: Resume, stage: str, error: Exception) -> None:
    resume.processing_status = f"{stage}_failed"
    resume.processing_error = str(error)
    await resume.save()


async def process_and_save_resume(
    filename: str,
    content_type: str | None,
    file_bytes: bytes,
    candidate_id: str,
    ai_service: AIService | None = None,
) -> ResumeResponse:
    """Persist an upload, then extract, parse, and summarize it stage by stage."""
    validate_resume_upload(filename, content_type, file_bytes)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    storage_path = UPLOAD_DIR / f"{uuid4().hex}_{Path(filename).name}"
    try:
        storage_path.write_bytes(file_bytes)
    except OSError as exc:
        raise ResumeUploadError("Could not store uploaded resume.") from exc

    try:
        resume = await resume_repo.create(
            Resume(
                candidate_id=PydanticObjectId(candidate_id),
                filename=Path(filename).name,
                file_path=str(storage_path),
                file_size_bytes=len(file_bytes),
            )
        )
    except Exception as exc:
        raise ResumeUploadError("Could not persist resume upload metadata.") from exc

    try:
        raw_text, page_count = extract_resume_text(file_bytes)
        resume.raw_text = raw_text
        resume.page_count = page_count
        resume.processing_status = "extracted"
        await resume.save()
    except ResumeExtractionError as exc:
        await _mark_failed(resume, "extraction", exc)
        raise

    client = ai_service or AIService()
    try:
        parsed = await parse_resume_text(raw_text, client)
        profile = await resume_profile_repo.create(
            ResumeProfile(
                resume_id=resume.id,
                candidate_id=resume.candidate_id,
                **parsed.model_dump(),
            )
        )
        resume.processing_status = "parsed"
        await resume.save()
    except ResumeParsingError as exc:
        await _mark_failed(resume, "parsing", exc)
        raise

    try:
        summary = await generate_resume_summary(parsed, client)
        profile.professional_summary = summary.professional_summary
        profile.key_highlights = summary.key_highlights
        profile.career_snapshot = summary.career_snapshot
        await resume_profile_repo.save(profile)
        resume.profile_id = profile.id
        resume.parsed_name = parsed.full_name
        resume.parsed_email = parsed.contact.email
        resume.parsed_phone = parsed.contact.phone
        resume.extracted_skills = parsed.skills
        resume.processing_status = "completed"
        await resume.save()
    except ResumeSummaryError as exc:
        await _mark_failed(resume, "summary", exc)
        raise

    await notification_service.create(
        candidate_id,
        "Resume intelligence ready",
        f"{filename} was parsed into a structured candidate profile.",
        "resume",
    )
    logger.info("Resume intelligence completed", extra={"resume_id": str(resume.id)})
    return _build_resume_response(resume)


async def list_candidate_resumes(candidate_id: str) -> list[ResumeResponse]:
    resumes = await resume_repo.list_by_candidate(candidate_id)
    return [_build_resume_response(resume) for resume in resumes]


async def get_resume_by_id(resume_id: str, candidate_id: str) -> ResumeResponse:
    resume = await resume_repo.get_by_id(resume_id)
    if not resume:
        raise EntityNotFoundError(entity="Resume", identifier=resume_id)
    if str(resume.candidate_id) != candidate_id:
        raise AuthorizationError(detail="You can only view your own uploaded resumes.")
    return _build_resume_response(resume)


async def update_resume_parsed_data(
    resume_id: str, candidate_id: str, payload: ResumeUpdateRequest
) -> ResumeResponse:
    """Persist human corrections to parsed email, phone, and extracted skills (Checklist #5)."""
    resume = await resume_repo.get_by_id(resume_id)
    if not resume:
        raise EntityNotFoundError(entity="Resume", identifier=resume_id)
    if str(resume.candidate_id) != candidate_id:
        raise AuthorizationError(detail="You can only edit your own uploaded resumes.")

    if payload.parsed_email is not None:
        resume.parsed_email = payload.parsed_email
    if payload.parsed_phone is not None:
        resume.parsed_phone = payload.parsed_phone
    if payload.extracted_skills is not None:
        resume.extracted_skills = payload.extracted_skills
        # Recalculate keyword density score if skills updated
        new_keyword_score = min(100, max(20, len(payload.extracted_skills) * 12))
        resume.quality_breakdown["keyword_density_score"] = new_keyword_score
        resume.ats_score = int(
            (resume.quality_breakdown["completeness_score"] * 0.3)
            + (new_keyword_score * 0.4)
            + (resume.quality_breakdown["formatting_score"] * 0.3)
        )

    await resume.save()
    logger.info("Persisted candidate AI correction for resume: %s", resume_id)
    return _build_resume_response(resume)


async def delete_resume(resume_id: str, candidate_id: str) -> None:
    resume = await resume_repo.get_by_id(resume_id)
    if not resume:
        raise EntityNotFoundError(entity="Resume", identifier=resume_id)
    if str(resume.candidate_id) != candidate_id:
        raise AuthorizationError(detail="You can only delete your own uploaded resumes.")
    storage_path = Path(resume.file_path)
    if storage_path.exists():
        storage_path.unlink()
    await resume_repo.delete(resume)
    logger.info("Resume deleted: %s", resume_id)
