"""Unit tests for Phase 9 deterministic statistical process bias audit logic."""

import unittest

from app.services.research_service import compute_statistical_process_audit


class TestBiasAuditStatisticalLogic(unittest.TestCase):

    def test_statistical_audit_normal_distribution(self):
        scores = [70.0, 75.0, 80.0, 85.0, 90.0]
        stats, flags, dominant_factors = compute_statistical_process_audit(scores)

        self.assertEqual(stats.mean, 80.0)
        self.assertEqual(stats.median, 80.0)
        self.assertEqual(stats.min_score, 70.0)
        self.assertEqual(stats.max_score, 90.0)
        self.assertEqual(len(flags), 0)

    def test_statistical_audit_high_variance_flag(self):
        # Synthetic dataset with high standard deviation (>22.0)
        scores = [10.0, 20.0, 85.0, 95.0, 100.0]
        stats, flags, dominant_factors = compute_statistical_process_audit(scores)

        self.assertTrue(stats.std_dev > 22.0)
        pattern_names = [f.pattern_name for f in flags]
        self.assertIn("High Variance in Applicant Pool", pattern_names)

    def test_statistical_audit_rejection_factor_dominance(self):
        scores = [60.0, 65.0, 70.0]
        rejection_counts = {
            "Distributed Systems": 8,  # 8 out of 10 total rejections (80%)
            "SQL": 2,
        }
        stats, flags, dominant_factors = compute_statistical_process_audit(scores, rejection_counts)

        self.assertEqual(len(dominant_factors), 2)
        self.assertEqual(dominant_factors[0]["factor_name"], "Distributed Systems")
        self.assertEqual(dominant_factors[0]["rejection_impact_percentage"], 80.0)

        pattern_names = [f.pattern_name for f in flags]
        self.assertIn("Single Factor Rejection Dominance", pattern_names)


if __name__ == "__main__":
    unittest.main()
