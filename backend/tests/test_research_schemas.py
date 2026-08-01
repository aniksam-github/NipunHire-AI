"""Unit tests for Phase 9 Research Pydantic schema validation & disclaimer enforcement."""

import unittest

from app.schemas.research import (
    ConsistencyMetrics,
    ExplanationTraceResponse,
    InterviewAnomalyFlag,
    InterviewCheatRiskResponse,
    ProcessBiasAuditResponse,
    ProcessPatternFlag,
    ResumeAnomalyCheckResponse,
    ResumeInconsistencyFlag,
    ScoreStatistics,
)


class TestResearchSchemas(unittest.TestCase):

    def test_explanation_trace_response_has_non_empty_disclaimer(self):
        metrics = ConsistencyMetrics(alignment_score=95.0, is_consistent=True, flagged_mismatches=[])
        trace = ExplanationTraceResponse(
            candidate_id="cand_123",
            job_id="job_123",
            consistency_metrics=metrics,
        )
        self.assertTrue(len(trace.human_review_disclaimer.strip()) > 0)
        self.assertIn("decision-support", trace.human_review_disclaimer.lower())

    def test_process_bias_audit_response_has_disclaimer_and_zero_demographic_fields(self):
        stats = ScoreStatistics(mean=75.0, median=76.0, std_dev=8.0, min_score=60.0, max_score=90.0)
        audit = ProcessBiasAuditResponse(
            job_id="job_123",
            total_applicants_audited=10,
            score_statistics=stats,
            flagged_process_patterns=[],
            dominant_rejection_factors=[],
        )
        self.assertTrue(len(audit.human_review_disclaimer.strip()) > 0)
        self.assertIn("zero demographic data", audit.human_review_disclaimer.lower())

        # Verify no protected demographic attribute fields exist anywhere in schema model fields
        schema_fields = set(ProcessBiasAuditResponse.model_fields.keys())
        demographic_keywords = {"race", "gender", "age", "ethnicity", "sex", "disability", "religion", "demographics"}
        self.assertTrue(schema_fields.isdisjoint(demographic_keywords))

    def test_resume_anomaly_response_has_disclaimer(self):
        flag = ResumeInconsistencyFlag(
            issue_type="overlapping_employment",
            description="Full-time role overlap",
            confidence_level="medium",
        )
        res = ResumeAnomalyCheckResponse(
            resume_id="res_123",
            candidate_id="cand_123",
            overall_risk_score=40,
            flagged_inconsistencies=[flag],
        )
        self.assertTrue(res.requires_human_review)
        self.assertTrue(len(res.human_review_disclaimer.strip()) > 0)

    def test_interview_cheat_risk_response_has_disclaimer(self):
        flag = InterviewAnomalyFlag(
            anomaly_type="phrasing_shift",
            turn_index=1,
            description="Sudden shift in vocabulary",
            confidence_level="high",
        )
        res = InterviewCheatRiskResponse(
            session_id="sess_123",
            candidate_id="cand_123",
            cheat_risk_score=30,
            risk_level="moderate",
            flagged_anomalies=[flag],
            supporting_reasoning="Shift between turns",
        )
        self.assertTrue(res.is_informational_only)
        self.assertTrue(len(res.human_review_disclaimer.strip()) > 0)


if __name__ == "__main__":
    unittest.main()
