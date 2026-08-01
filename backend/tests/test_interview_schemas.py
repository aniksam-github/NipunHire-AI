"""Unit tests for Phase 6 Interview AI Pydantic schema validation."""

import unittest
from pydantic import ValidationError

from app.schemas.interview import (
    AdaptiveNextQuestionResponse,
    AnswerEvaluation,
    DifficultyAdjustment,
    DifficultyDecision,
    DifficultyLevel,
    DimensionScore,
    GeneratedQuestionList,
    HiringRecommendation,
    IdealAnswerComparison,
    InterviewQuestion,
    InterviewReport,
    QuestionCategory,
    SessionStatus,
)


class TestInterviewSchemas(unittest.TestCase):

    def test_session_status_enum(self):
        self.assertEqual(SessionStatus.IN_PROGRESS.value, "in_progress")
        self.assertEqual(SessionStatus.READY_TO_COMPLETE.value, "ready_to_complete")
        self.assertEqual(SessionStatus.COMPLETED.value, "completed")
        self.assertEqual(SessionStatus.ABANDONED.value, "abandoned")

    def test_module_1_generated_question_schema(self):
        q = InterviewQuestion(
            question_text="How do you design a scalable microservices architecture in Python?",
            category=QuestionCategory.TECHNICAL,
            difficulty=DifficultyLevel.HARD,
        )
        self.assertEqual(q.difficulty, DifficultyLevel.HARD)
        self.assertEqual(q.category, QuestionCategory.TECHNICAL)

        questions_list = GeneratedQuestionList(questions=[q])
        self.assertEqual(len(questions_list.questions), 1)

    def test_module_1_invalid_difficulty_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            InterviewQuestion(
                question_text="Tell me about yourself",
                category="behavioral",
                difficulty="super_hard",
            )

    def test_module_3_answer_evaluation_schema_bounded_scores(self):
        dim = DimensionScore(score=9, justification="Clear explanation of async locking")
        self.assertEqual(dim.score, 9)

        # Test score bounds (must be 0 <= score <= 10)
        with self.assertRaises(ValidationError):
            DimensionScore(score=11, justification="Exceeds max score")

        with self.assertRaises(ValidationError):
            DimensionScore(score=-1, justification="Below min score")

        evaluation = AnswerEvaluation(
            technical_correctness=DimensionScore(score=9, justification="Accurate"),
            communication_clarity=DimensionScore(score=8, justification="Structured"),
            confidence=DimensionScore(score=7, justification="Confident posture"),
            grammar=DimensionScore(score=10, justification="Impeccable syntax"),
            completeness=DimensionScore(score=8, justification="Covered core aspects"),
            overall_turn_score=84,
            overall_feedback="Solid performance on technical question",
        )
        self.assertEqual(evaluation.overall_turn_score, 84)

    def test_module_3_invalid_overall_score_bounds(self):
        with self.assertRaises(ValidationError):
            AnswerEvaluation(
                technical_correctness=DimensionScore(score=5, justification="Ok"),
                communication_clarity=DimensionScore(score=5, justification="Ok"),
                confidence=DimensionScore(score=5, justification="Ok"),
                grammar=DimensionScore(score=5, justification="Ok"),
                completeness=DimensionScore(score=5, justification="Ok"),
                overall_turn_score=105,  # Invalid (>100)
                overall_feedback="Invalid score test",
            )

    def test_module_4_ideal_answer_comparison_schema(self):
        comparison = IdealAnswerComparison(
            ideal_answer="An ideal answer would state how async event loops prevent I/O blocking...",
            key_strengths=["Identified async non-blocking benefit"],
            missing_points=["Did not discuss memory consumption or concurrency limits"],
            comparison_summary="Strong answer but missed low-level GIL trade-offs.",
        )
        self.assertEqual(len(comparison.key_strengths), 1)
        self.assertEqual(len(comparison.missing_points), 1)

    def test_module_2_adaptive_next_question_schema(self):
        response = AdaptiveNextQuestionResponse(
            difficulty_decision=DifficultyDecision.INCREASE,
            reasoning="Candidate answered easy technical question with ease.",
            next_difficulty=DifficultyLevel.HARD,
            next_question=InterviewQuestion(
                question_text="Explain distributed consensus algorithms like Raft.",
                category=QuestionCategory.TECHNICAL,
                difficulty=DifficultyLevel.HARD,
            ),
        )
        self.assertEqual(response.difficulty_decision, DifficultyDecision.INCREASE)
        self.assertEqual(response.next_difficulty, DifficultyLevel.HARD)

    def test_module_5_interview_report_schema(self):
        report = InterviewReport(
            overall_score=88,
            strengths=["Excellent problem solving", "Clear communication"],
            weaknesses=["Could provide more concrete metrics for past achievements"],
            hiring_recommendation=HiringRecommendation.STRONG_HIRE,
            summary_justification="Candidate demonstrated high proficiency across all turns.",
            category_breakdown={
                "technical_correctness": 9.0,
                "communication_clarity": 8.5,
                "confidence": 8.0,
                "grammar": 9.5,
                "completeness": 8.5,
            },
        )
        self.assertEqual(report.hiring_recommendation, HiringRecommendation.STRONG_HIRE)
        self.assertEqual(report.overall_score, 88)


if __name__ == "__main__":
    unittest.main()
