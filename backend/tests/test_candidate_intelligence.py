import asyncio
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from pydantic import ValidationError

from app.schemas.candidate_intelligence import (
    ATSOptimizerRequest,
    ATSOptimizerResult,
    CareerCoachResult,
    ResumeOptimizerRequest,
    ResumeOptimizerResult,
    ResumeTextSection,
)
from app.schemas.resume_intelligence import ResumeParsingResult
from app.services import coach_service
from app.services import candidate_intelligence_service


class FakeAIService:
    def __init__(self, result):
        self.result = result
        self.calls = []

    async def get_structured_response(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


class CandidateIntelligenceSchemaTests(unittest.TestCase):
    def test_career_coach_requires_advice(self):
        with self.assertRaises(ValidationError):
            CareerCoachResult(career_advice="")

    def test_resume_optimizer_requires_at_least_one_section(self):
        with self.assertRaises(ValidationError):
            ResumeOptimizerRequest(resume_id="resume", sections=[])

    def test_ats_result_rejects_invalid_phrase_shape(self):
        with self.assertRaises(ValidationError):
            ATSOptimizerResult(phrasing_adjustments=[{"original_phrase": "Python"}])


from unittest.mock import AsyncMock, MagicMock, patch


class CandidateIntelligenceServiceTests(unittest.TestCase):
    def setUp(self):
        self.collection_patcher = patch("beanie.Document.get_pymongo_collection", return_value=MagicMock())
        self.collection_patcher.start()

    def tearDown(self):
        self.collection_patcher.stop()

    def test_resume_optimizer_persists_review_only_suggestion(self):
        request = ResumeOptimizerRequest(
            resume_id="resume-id",
            sections=[ResumeTextSection(label="Experience", text="Worked on API features.")],
        )
        ai = FakeAIService(
            ResumeOptimizerResult(
                rewrites=[
                    {
                        "original_text": "Worked on API features.",
                        "suggested_rewrite": "Developed API features supporting the product team.",
                    }
                ]
            )
        )
        resume = SimpleNamespace(id="507f1f77bcf86cd799439012")
        stored = SimpleNamespace(id="suggestion-id", created_at=datetime.now(timezone.utc))
        with patch.object(
            candidate_intelligence_service,
            "_get_profile_for_candidate",
            AsyncMock(return_value=(resume, SimpleNamespace())),
        ), patch.object(
            candidate_intelligence_service.candidate_intelligence_repo,
            "create_resume_suggestion",
            AsyncMock(return_value=stored),
        ) as create:
            response = asyncio.run(
                candidate_intelligence_service.generate_resume_optimization(request, "507f1f77bcf86cd799439011", ai)
            )
        self.assertEqual(response.rewrites[0].original_text, request.sections[0].text)
        self.assertEqual(response.id, "suggestion-id")
        self.assertEqual(ai.calls[0]["response_model"], ResumeOptimizerResult)
        self.assertEqual(create.await_count, 1)

    def test_resume_optimizer_rejects_response_without_comparable_original(self):
        request = ResumeOptimizerRequest(
            resume_id="resume-id", sections=[ResumeTextSection(label="Project", text="Built a tool.")]
        )
        ai = FakeAIService(
            ResumeOptimizerResult(rewrites=[{"original_text": "Different text", "suggested_rewrite": "Built a tool."}])
        )
        with patch.object(
            candidate_intelligence_service,
            "_get_profile_for_candidate",
            AsyncMock(return_value=(SimpleNamespace(id="resume"), SimpleNamespace())),
        ):
            with self.assertRaisesRegex(Exception, "preserve each submitted original"):
                asyncio.run(candidate_intelligence_service.generate_resume_optimization(request, "507f1f77bcf86cd799439011", ai))

    def test_ats_optimizer_uses_profile_and_job_with_mocked_ai(self):
        candidate_id = "507f1f77bcf86cd799439011"
        resume = SimpleNamespace(id="507f1f77bcf86cd799439012")
        profile = SimpleNamespace(
            model_dump=lambda **_: ResumeParsingResult(full_name="Jane", skills=["Python"]).model_dump()
        )
        job = SimpleNamespace(
            id="507f1f77bcf86cd799439013",
            model_dump=lambda **_: {"title": "Backend Engineer", "description": "Docker required"},
        )
        result = ATSOptimizerResult(
            missing_keywords=["Docker"],
            phrasing_adjustments=[
                {"original_phrase": "Built APIs", "suggested_phrase": "Built Python APIs", "rationale": "Python is evidenced."}
            ],
        )
        stored = SimpleNamespace(id="suggestion-id", created_at=datetime.now(timezone.utc))
        with patch.object(candidate_intelligence_service, "_get_profile_for_candidate", AsyncMock(return_value=(resume, profile))), patch.object(
            candidate_intelligence_service.job_repo, "get_by_id", AsyncMock(return_value=job)
        ), patch.object(
            candidate_intelligence_service.candidate_intelligence_repo, "create_ats_suggestion", AsyncMock(return_value=stored)
        ):
            response = asyncio.run(
                candidate_intelligence_service.generate_ats_optimization(
                    ATSOptimizerRequest(resume_id="resume", job_id="job"), candidate_id, FakeAIService(result)
                )
            )
        self.assertEqual(response.missing_keywords, ["Docker"])

    def test_career_plan_uses_existing_profile_and_mocked_ai(self):
        candidate_id = "507f1f77bcf86cd799439011"
        resume = SimpleNamespace(id="507f1f77bcf86cd799439012")
        profile = SimpleNamespace(
            id="507f1f77bcf86cd799439014",
            model_dump=lambda **_: ResumeParsingResult(full_name="Jane", skills=["Python"]).model_dump(),
        )
        result = CareerCoachResult(career_advice="Build evidence for your target role.")
        stored = SimpleNamespace(id="plan-id", created_at=datetime.now(timezone.utc))
        with patch.object(coach_service, "_get_candidate_profile", AsyncMock(return_value=(resume, profile))), patch.object(
            coach_service.resume_screening_repo, "get_by_profile_id", AsyncMock(return_value=None)
        ), patch.object(coach_service.matching_repo, "list_recent_by_candidate", AsyncMock(return_value=[])), patch.object(
            coach_service.coach_repo, "create", AsyncMock(return_value=stored)
        ):
            response = asyncio.run(
                coach_service.generate_plan(candidate_id, coach_service.CareerCoachAnalysisRequest(), FakeAIService(result))
            )
        self.assertEqual(response.career_advice, result.career_advice)


if __name__ == "__main__":
    unittest.main()
