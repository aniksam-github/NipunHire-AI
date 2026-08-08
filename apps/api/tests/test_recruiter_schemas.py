"""Unit tests for Phase 8 Recruiter AI Pydantic schema validation."""

import unittest
from pydantic import ValidationError

from app.schemas.recruiter import (
    AggregateHiringRecommendationResponse,
    CandidateComparisonEntry,
    CandidateComparisonResult,
    CandidateRankingList,
    CandidateSummaryReport,
    GeneratedJobDescription,
    RankedCandidateEntry,
    RankingWeights,
    RecruiterInterviewHighlight,
    RecruiterInterviewSummaryResponse,
)
from app.schemas.resume_matching import RecruiterRecommendation


class TestRecruiterSchemas(unittest.TestCase):

    def test_candidate_summary_report_schema(self):
        summary = CandidateSummaryReport(
            candidate_id="cand_123",
            key_highlights=["Strong Python & FastAPI background"],
            overall_assessment="High potential candidate across all phases.",
            standout_signals={"interview": ["Excellent communication"], "coding": ["Optimal O(N) complexity"]},
            available_data_sources=["resume_match", "interview_report", "coding_review"],
        )
        self.assertEqual(summary.candidate_id, "cand_123")
        self.assertEqual(len(summary.available_data_sources), 3)

    def test_ranking_weights_validation(self):
        weights = RankingWeights(match_weight=0.5, interview_weight=0.3, coding_weight=0.2)
        self.assertEqual(weights.match_weight, 0.5)

        with self.assertRaises(ValidationError):
            RankingWeights(match_weight=-0.1, interview_weight=0.5, coding_weight=0.5)

    def test_ranked_candidate_entry_schema(self):
        entry = RankedCandidateEntry(
            rank=1,
            candidate_id="cand_123",
            composite_score=87.5,
            sub_scores={"match_score": 85.0, "interview_score": 90.0, "coding_score": 88.0},
            justification="Ranked #1 due to strong scores across all phases.",
        )
        self.assertEqual(entry.rank, 1)
        self.assertEqual(entry.composite_score, 87.5)

    def test_recruiter_interview_summary_schema(self):
        highlight = RecruiterInterviewHighlight(
            turn_index=0,
            question_text="Explain GIL",
            category="technical",
            candidate_answer_summary="CPython execution lock...",
            turn_score=85,
        )
        summary = RecruiterInterviewSummaryResponse(
            session_id="sess_123",
            candidate_id="cand_123",
            overall_score=85,
            hiring_recommendation="Hire",
            status="completed",
            key_qa_highlights=[highlight],
        )
        self.assertEqual(summary.key_qa_highlights[0].turn_score, 85)

    def test_aggregate_hiring_recommendation_schema(self):
        recommendation = AggregateHiringRecommendationResponse(
            candidate_id="cand_123",
            recommendation=RecruiterRecommendation.HIRE,
            confidence_score=92,
            grounded_reason="High match score (85%) and strong coding review (90%).",
            key_factors=["Optimal coding algorithm", "High interview score"],
        )
        self.assertEqual(recommendation.recommendation, RecruiterRecommendation.HIRE)
        self.assertEqual(recommendation.confidence_score, 92)

    def test_generated_job_description_schema(self):
        jd = GeneratedJobDescription(
            role_title="Senior Python Engineer",
            seniority_level="Senior",
            summary="Lead backend developer for AI platform...",
            responsibilities=["Build high-throughput APIs"],
            required_qualifications=["5+ years Python"],
            preferred_qualifications=["MongoDB experience"],
        )
        self.assertEqual(jd.role_title, "Senior Python Engineer")
        self.assertEqual(len(jd.responsibilities), 1)


if __name__ == "__main__":
    unittest.main()
