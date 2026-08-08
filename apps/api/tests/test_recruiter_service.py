"""Unit tests for Phase 8 Recruiter AI service logic using mocked AIService."""

import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from beanie import PydanticObjectId

from app.models.interview import InterviewQuestionModel, InterviewSession, SessionStatus
from app.schemas.recruiter import (
    AggregateHiringRecommendationResponse,
    CandidateComparisonEntry,
    CandidateComparisonRequest,
    CandidateComparisonResult,
    CandidateSummaryReport,
    GeneratedJobDescription,
    JobDescriptionGenerateRequest,
)
from app.schemas.resume_matching import RecruiterRecommendation
from app.services import recruiter_service


class FakeAIService:
    def __init__(self, responses: list[object]):
        self.responses = responses
        self.call_history: list[dict] = []

    async def get_structured_response(self, **kwargs):
        self.call_history.append(kwargs)
        if not self.responses:
            raise RuntimeError("No fake response remaining in queue")
        return self.responses.pop(0)


class TestRecruiterService(unittest.TestCase):

    def test_generate_candidate_summary(self):
        candidate_id = "507f1f77bcf86cd799439011"
        fake_summary = CandidateSummaryReport(
            candidate_id=candidate_id,
            key_highlights=["5+ years Python", "Strong interview performance"],
            overall_assessment="High suitability candidate.",
            standout_signals={"interview": ["Clear communication"]},
            available_data_sources=["resume_match", "interview_report"],
        )
        ai = FakeAIService([fake_summary])

        with patch.object(recruiter_service, "_get_candidate_context_bundle", AsyncMock(return_value={
            "candidate_id": candidate_id,
            "profile_json": '{"name": "Alice"}',
            "match_json": '{"match_score": 85}',
            "interview_json": '{"overall_score": 90}',
            "coding_json": "None",
        })):
            res = asyncio.run(recruiter_service.generate_candidate_summary(candidate_id, ai_service=ai))
            self.assertEqual(res.candidate_id, candidate_id)
            self.assertEqual(res.overall_assessment, "High suitability candidate.")

    def test_compare_candidates(self):
        job_id = "507f1f77bcf86cd799439012"
        c1, c2 = "507f1f77bcf86cd799439011", "507f1f77bcf86cd799439022"

        fake_comp = CandidateComparisonResult(
            job_id=job_id,
            candidates_compared=[c1, c2],
            per_candidate_breakdown=[
                CandidateComparisonEntry(candidate_id=c1, full_name="Alice", relative_strengths=["Better Python"], dimension_ratings={"technical": 9.0}),
                CandidateComparisonEntry(candidate_id=c2, full_name="Bob", relative_strengths=["Better SQL"], dimension_ratings={"technical": 8.0}),
            ],
            dimension_leaders={"technical": c1},
            comparison_summary="Alice leads technically, Bob leads on database experience.",
        )
        ai = FakeAIService([fake_comp])

        mock_job = SimpleNamespace(id=PydanticObjectId(job_id), title="Backend Role", department="Eng", required_skills=["Python"], model_dump=lambda **_: {"title": "Backend Role"})

        with patch.object(recruiter_service.job_repo, "get_by_id", AsyncMock(return_value=mock_job)), \
             patch.object(recruiter_service, "_get_candidate_context_bundle", AsyncMock(return_value={
                 "candidate_id": c1, "profile_json": "{}", "match_json": "{}", "interview_json": "{}", "coding_json": "{}",
                 "raw_match": {}, "raw_interview": {}, "raw_coding": {}
             })):
            res = asyncio.run(
                recruiter_service.compare_candidates(
                    CandidateComparisonRequest(job_id=job_id, candidate_ids=[c1, c2]),
                    ai_service=ai,
                )
            )
            self.assertEqual(res.dimension_leaders["technical"], c1)

    def test_get_recruiter_interview_summary(self):
        session_id = "507f1f77bcf86cd799439033"
        candidate_id = "507f1f77bcf86cd799439011"

        mock_session = InterviewSession.model_construct(
            id=PydanticObjectId(session_id),
            candidate_id=PydanticObjectId(candidate_id),
            job_id=None,
            overall_score=88,
            status=SessionStatus.COMPLETED,
            turns=[],
            final_report=None,
        )

        with patch.object(InterviewSession, "get_pymongo_collection", return_value=MagicMock()), \
             patch.object(recruiter_service.interview_repo, "get_session_by_id", AsyncMock(return_value=mock_session)):
            res = asyncio.run(recruiter_service.get_recruiter_interview_summary(session_id))
            self.assertEqual(res.session_id, session_id)
            self.assertEqual(res.overall_score, 88)

    def test_generate_aggregate_hiring_recommendation(self):
        candidate_id = "507f1f77bcf86cd799439011"
        fake_rec = AggregateHiringRecommendationResponse(
            candidate_id=candidate_id,
            recommendation=RecruiterRecommendation.HIRE,
            confidence_score=90,
            grounded_reason="High interview (90%) and coding score (88%).",
            key_factors=["Strong interview accuracy"],
        )
        fake_summary = CandidateSummaryReport(
            candidate_id=candidate_id,
            key_highlights=[],
            overall_assessment="Good profile",
            standout_signals={},
            available_data_sources=[],
        )
        ai = FakeAIService([fake_summary, fake_rec])

        with patch.object(recruiter_service, "_get_candidate_context_bundle", AsyncMock(return_value={
            "candidate_id": candidate_id, "profile_json": "{}", "match_json": "{}", "interview_json": "{}", "coding_json": "{}",
            "raw_match": {}, "raw_interview": {}, "raw_coding": {}
        })):
            res = asyncio.run(
                recruiter_service.generate_aggregate_hiring_recommendation(candidate_id, ai_service=ai)
            )
            self.assertEqual(res.recommendation, RecruiterRecommendation.HIRE)
            self.assertEqual(res.confidence_score, 90)

    def test_generate_job_description(self):
        fake_jd = GeneratedJobDescription(
            role_title="Lead Python Architect",
            seniority_level="Lead",
            summary="Lead architect position for enterprise platform...",
            responsibilities=["Architecture design"],
            required_qualifications=["Python", "FastAPI"],
            preferred_qualifications=["AWS"],
        )
        ai = FakeAIService([fake_jd])

        res = asyncio.run(
            recruiter_service.generate_job_description(
                JobDescriptionGenerateRequest(role_title="Lead Python Architect", required_skills=["Python", "FastAPI"], seniority_level="Lead"),
                ai_service=ai,
            )
        )
        self.assertEqual(res.role_title, "Lead Python Architect")
        self.assertEqual(len(res.required_qualifications), 2)


if __name__ == "__main__":
    unittest.main()
