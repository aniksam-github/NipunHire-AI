import asyncio
import unittest

import fitz

from app.schemas.resume_intelligence import ResumeParsingResult, ResumeSummaryResult
from app.services.resume_service import (
    MAX_RESUME_FILE_SIZE_BYTES,
    extract_resume_text,
    generate_resume_summary,
    parse_resume_text,
    validate_resume_upload,
)
from app.core.resume_exceptions import ResumeUploadError


class FakeAIService:
    def __init__(self):
        self.calls = []

    async def get_structured_response(self, **kwargs):
        self.calls.append(kwargs)
        if kwargs["response_model"] is ResumeParsingResult:
            return ResumeParsingResult.model_validate(
                {
                    "full_name": "Jane Doe",
                    "contact": {"email": "jane@example.com"},
                    "skills": ["Python"],
                    "education": [],
                    "projects": [],
                    "experience": [],
                }
            )
        return ResumeSummaryResult(
            professional_summary="Backend engineer.",
            key_highlights=["Python"],
            career_snapshot="Early-career engineer.",
        )


class ResumeIntelligenceTests(unittest.TestCase):
    def test_rejects_non_pdf_upload(self):
        with self.assertRaises(ResumeUploadError):
            validate_resume_upload("resume.txt", "text/plain", b"not a PDF")

    def test_rejects_oversized_upload(self):
        with self.assertRaises(ResumeUploadError):
            validate_resume_upload(
                "resume.pdf",
                "application/pdf",
                b"%PDF-" + b"x" * MAX_RESUME_FILE_SIZE_BYTES,
            )

    def test_extracts_text_from_pdf_bytes(self):
        document = fitz.open()
        document.new_page().insert_text((72, 72), "NipunHire test resume")
        text, page_count = extract_resume_text(document.tobytes())
        document.close()
        self.assertEqual(page_count, 1)
        self.assertIn("NipunHire test resume", text)

    def test_mocked_ai_parser_and_summary_match_schemas(self):
        service = FakeAIService()
        parsed = asyncio.run(parse_resume_text("Jane Doe Python", service))
        summary = asyncio.run(generate_resume_summary(parsed, service))
        self.assertIsInstance(parsed, ResumeParsingResult)
        self.assertIsInstance(summary, ResumeSummaryResult)
        self.assertEqual(len(service.calls), 2)


if __name__ == "__main__":
    unittest.main()
