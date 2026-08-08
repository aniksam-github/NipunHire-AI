"""Unit tests for Phase 9 Research service logic using mocked AIService."""

import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from beanie import PydanticObjectId

from app.models.research import InterviewCheatRiskReport, ResumeAnomalyReport
from app.schemas.research import (
    InterviewAnomalyFlag,
    InterviewCheatRiskResponse,
    ResumeAnomalyCheckResponse,
    ResumeInconsistencyFlag,
)
from app.services import research_service
from app.services.research_service import compute_consistency_metrics


class FakeAIService:
    def __init__(self, responses: list[object]):
        self.responses = responses
        self.call_history: list[dict] = []

    async def get_structured_response(self, **kwargs):
        self.call_history.append(kwargs)
        if not self.responses:
            raise RuntimeError("No fake response remaining in queue")
        return self.responses.pop(0)


class TestResearchService(unittest.TestCase):

    def test_compute_consistency_metrics_detects_mismatch(self):
        metrics = compute_consistency_metrics(match_score=85.0, interview_score=45.0, coding_score=80.0)
        self.assertFalse(metrics.is_consistent)
        self.assertTrue(len(metrics.flagged_mismatches) > 0)
        self.assertIn("conflicts with low interview performance", metrics.flagged_mismatches[0])

    def test_compute_consistency_metrics_aligned_scores(self):
        metrics = compute_consistency_metrics(match_score=85.0, interview_score=88.0, coding_score=82.0)
        self.assertTrue(metrics.is_consistent)
        self.assertEqual(len(metrics.flagged_mismatches), 0)

    def test_check_resume_anomalies(self):
        candidate_id = "507f1f77bcf86cd799439011"
        resume_id = "507f1f77bcf86cd799439022"

        fake_res = ResumeAnomalyCheckResponse(
            resume_id=resume_id,
            candidate_id=candidate_id,
            overall_risk_score=35,
            flagged_inconsistencies=[
                ResumeInconsistencyFlag(
                    issue_type="overlapping_employment",
                    description="Simultaneous full-time roles claimed",
                    confidence_level="medium",
                    supporting_evidence="Dates 2020-2022 at two companies",
                )
            ],
            requires_human_review=True,
        )
        ai = FakeAIService([fake_res])

        with patch.object(ResumeAnomalyReport, "get_pymongo_collection", return_value=MagicMock()), \
             patch.object(research_service.resume_repo, "get_by_id", AsyncMock(return_value=None)), \
             patch.object(research_service.resume_profile_repo, "get_by_resume_id", AsyncMock(return_value=None)), \
             patch.object(research_service.research_repo, "create_resume_anomaly_report", AsyncMock(side_effect=lambda r: r)):

            res = asyncio.run(research_service.check_resume_anomalies(candidate_id, resume_id, ai_service=ai))
            self.assertEqual(res.overall_risk_score, 35)
            self.assertEqual(res.flagged_inconsistencies[0].issue_type, "overlapping_employment")
            self.assertTrue(len(res.human_review_disclaimer) > 0)

    def test_detect_interview_cheat_risk(self):
        candidate_id = "507f1f77bcf86cd799439011"
        session_id = "507f1f77bcf86cd799439033"

        fake_res = InterviewCheatRiskResponse(
            session_id=session_id,
            candidate_id=candidate_id,
            cheat_risk_score=25,
            risk_level="low",
            flagged_anomalies=[
                InterviewAnomalyFlag(
                    anomaly_type="phrasing_shift",
                    turn_index=1,
                    description="Shift in answer detail",
                    confidence_level="low",
                )
            ],
            supporting_reasoning="Minor shift observed across turns",
            is_informational_only=True,
        )
        ai = FakeAIService([fake_res])

        mock_session = SimpleNamespace(
            id=PydanticObjectId(session_id),
            candidate_id=PydanticObjectId(candidate_id),
            turns=[
                SimpleNamespace(
                    turn_index=0,
                    question=SimpleNamespace(question_text="Explain locks", difficulty=SimpleNamespace(value="medium")),
                    candidate_answer="Locks control concurrency",
                    evaluation=SimpleNamespace(overall_turn_score=80),
                )
            ],
        )

        with patch.object(InterviewCheatRiskReport, "get_pymongo_collection", return_value=MagicMock()), \
             patch.object(research_service.interview_repo, "get_session_by_id", AsyncMock(return_value=mock_session)), \
             patch.object(research_service.research_repo, "create_interview_cheat_report", AsyncMock(side_effect=lambda r: r)):

            res = asyncio.run(research_service.detect_interview_cheat_risk(candidate_id, session_id, ai_service=ai))
            self.assertEqual(res.cheat_risk_score, 25)
            self.assertTrue(res.is_informational_only)
            self.assertTrue(len(res.human_review_disclaimer) > 0)


if __name__ == "__main__":
    unittest.main()
