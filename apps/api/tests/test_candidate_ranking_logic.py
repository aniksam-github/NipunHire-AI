"""Unit tests for Phase 8 deterministic candidate ranking calculation logic."""

import unittest

from app.schemas.recruiter import RankingWeights
from app.services.recruiter_service import compute_deterministic_composite_score


class TestCandidateRankingLogic(unittest.TestCase):

    def test_composite_score_all_three_scores_present(self):
        weights = RankingWeights(match_weight=0.4, interview_weight=0.35, coding_weight=0.25)
        sub_scores = {
            "match_score": 80.0,
            "interview_score": 90.0,
            "coding_score": 100.0,
        }
        # Expected: (80 * 0.4) + (90 * 0.35) + (100 * 0.25) = 32 + 31.5 + 25 = 88.5
        score = compute_deterministic_composite_score(sub_scores, weights)
        self.assertEqual(score, 88.5)

    def test_composite_score_dynamic_weight_normalization_missing_one_score(self):
        weights = RankingWeights(match_weight=0.4, interview_weight=0.35, coding_weight=0.25)
        # Candidate has match_score (80) and coding_score (100), but NO interview_score (None)
        sub_scores = {
            "match_score": 80.0,
            "interview_score": None,
            "coding_score": 100.0,
        }
        # Available weights: match=0.4, coding=0.25 (sum = 0.65)
        # Normalized weights: match = 0.4 / 0.65 = 0.61538, coding = 0.25 / 0.65 = 0.384615
        # Composite score = (80 * (0.4/0.65)) + (100 * (0.25/0.65)) = 49.2307 + 38.4615 = 87.69
        score = compute_deterministic_composite_score(sub_scores, weights)
        self.assertEqual(score, 87.69)

    def test_composite_score_single_score_present(self):
        weights = RankingWeights(match_weight=0.4, interview_weight=0.35, coding_weight=0.25)
        sub_scores = {
            "match_score": 95.0,
            "interview_score": None,
            "coding_score": None,
        }
        # Only match_score available -> normalized weight = 1.0 -> composite = 95.0
        score = compute_deterministic_composite_score(sub_scores, weights)
        self.assertEqual(score, 95.0)

    def test_composite_score_no_scores_present(self):
        weights = RankingWeights(match_weight=0.4, interview_weight=0.35, coding_weight=0.25)
        sub_scores = {
            "match_score": None,
            "interview_score": None,
            "coding_score": None,
        }
        score = compute_deterministic_composite_score(sub_scores, weights)
        self.assertEqual(score, 0.0)


if __name__ == "__main__":
    unittest.main()
