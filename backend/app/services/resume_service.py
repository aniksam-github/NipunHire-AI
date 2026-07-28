"""
Resume Service — orchestrates file storage, PyMuPDF extraction, parsing,
ATS scoring, and DB persistence for candidate PDF resumes.
"""

import os
from pathlib import Path
import logging
from beanie import PydanticObjectId

from app.core.exceptions import EntityNotFoundError, AuthorizationError
from app.models.resume import Resume
from app.repositories import resume_repo
from app.schemas.resume import ResumeResponse, QualityBreakdownSchema, AIFeedbackSchema
from app.services import pdf_service, resume_parser_service
from app.services import notification_service

logger = logging.getLogger(__name__)

# Upload Storage Directory
UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _build_resume_response(resume: Resume) -> ResumeResponse:
    """Maps a Resume document to a ResumeResponse schema."""
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


async def process_and_save_resume(
    filename: str,
    file_bytes: bytes,
    candidate_id: str,
) -> ResumeResponse:
    """
    Saves PDF file to disk, extracts text using PyMuPDF, parses skills & contact info,
    calculates ATS health score, and saves Resume document in MongoDB.
    """
    # 1. PyMuPDF Text & Page Count Extraction
    raw_text, page_count = pdf_service.extract_text_from_pdf_bytes(file_bytes)

    # 2. Contact & Skills Parsing
    email = resume_parser_service.extract_email(raw_text)
    phone = resume_parser_service.extract_phone(raw_text)
    skills = resume_parser_service.extract_skills(raw_text)

    # 3. ATS Health Metrics & Quality Breakdown
    ats_score, quality_breakdown, ai_feedback = resume_parser_service.calculate_ats_metrics(
        text=raw_text,
        extracted_email=email,
        extracted_phone=phone,
        skills=skills,
        page_count=page_count,
    )

    # 4. Save file to disk
    cand_oid = PydanticObjectId(candidate_id)
    dest_path = UPLOAD_DIR / f"{candidate_id}_{int(os.path.getmtime('.'))}_{filename}"
    with open(dest_path, "wb") as f:
        f.write(file_bytes)

    # 5. Save Document in MongoDB
    resume = Resume(
        candidate_id=cand_oid,
        filename=filename,
        file_path=str(dest_path),
        file_size_bytes=len(file_bytes),
        page_count=page_count,
        raw_text=raw_text,
        parsed_email=email,
        parsed_phone=phone,
        extracted_skills=skills,
        ats_score=ats_score,
        quality_breakdown=quality_breakdown,
        ai_feedback=ai_feedback,
    )

    resume = await resume_repo.create(resume)
    await notification_service.create(candidate_id, "Resume analysis ready", f"{filename} received an ATS score of {ats_score}%.", "resume")
    logger.info("Resume processed & saved: %s (ATS Score: %d)", filename, ats_score)
    return _build_resume_response(resume)


async def list_candidate_resumes(candidate_id: str) -> list[ResumeResponse]:
    """Lists all resumes uploaded by a candidate."""
    resumes = await resume_repo.list_by_candidate(candidate_id)
    return [_build_resume_response(r) for r in resumes]


async def get_resume_by_id(resume_id: str, candidate_id: str) -> ResumeResponse:
    """Fetches a specific resume analysis."""
    resume = await resume_repo.get_by_id(resume_id)
    if not resume:
        raise EntityNotFoundError(entity="Resume", identifier=resume_id)
    if str(resume.candidate_id) != candidate_id:
        raise AuthorizationError(detail="You can only view your own uploaded resumes.")
    return _build_resume_response(resume)


async def delete_resume(resume_id: str, candidate_id: str) -> None:
    """Deletes a candidate's uploaded resume."""
    resume = await resume_repo.get_by_id(resume_id)
    if not resume:
        raise EntityNotFoundError(entity="Resume", identifier=resume_id)
    if str(resume.candidate_id) != candidate_id:
        raise AuthorizationError(detail="You can only delete your own uploaded resumes.")

    # Remove disk file if exists
    if os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except Exception:
            pass

    await resume_repo.delete(resume)
    logger.info("Resume deleted: %s", resume_id)
