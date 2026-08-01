"""Unit tests for Phase 7 Coding AI Pydantic schema validation."""

import unittest
from pydantic import ValidationError

from app.models.coding import CodingDifficulty, CodingLanguage
from app.schemas.coding import (
    CodingExample,
    CodingQuestion,
    CodingQuestionGenerated,
    CodingQuestionGenerateRequest,
    CodingReviewResult,
    CodingSubmissionCreate,
    ConsolidatedCodingFeedbackResponse,
)


class TestCodingSchemas(unittest.TestCase):

    def test_coding_question_schema(self):
        ex = CodingExample(input="[2, 7, 11, 15], target=9", output="[0, 1]", explanation="nums[0] + nums[1] == 9")
        q = CodingQuestion(
            id="q123",
            title="Two Sum",
            problem_statement="Given an array of integers nums and an integer target, return indices of two numbers...",
            input_output_format="nums: List[int], target: int -> List[int]",
            examples=[ex],
            constraints=["2 <= nums.length <= 10^4"],
            difficulty=CodingDifficulty.EASY,
            topics=["arrays", "hash-tables"],
            starter_code="def two_sum(nums, target):\n    pass",
        )
        self.assertEqual(q.difficulty, CodingDifficulty.EASY)
        self.assertEqual(len(q.examples), 1)

    def test_coding_review_result_schema_bounded_scores(self):
        review = CodingReviewResult(
            correctness_score=90,
            code_quality_score=85,
            overall_score=88,
            correctness_assessment="Identified linear solution using hash map.",
            is_incomplete_or_invalid=False,
            identified_bugs=["No check for duplicate elements if allowed"],
            time_complexity="O(N)",
            space_complexity="O(N)",
            complexity_explanation="Single pass through array storing values in hash map.",
            code_quality_observations=["Clean naming conventions"],
            optimization_suggestions=["Consider pre-allocating dictionary size"],
        )
        self.assertEqual(review.overall_score, 88)
        self.assertEqual(review.time_complexity, "O(N)")

    def test_coding_review_invalid_score_bounds_raises_error(self):
        with self.assertRaises(ValidationError):
            CodingReviewResult(
                correctness_score=105,  # Invalid (>100)
                code_quality_score=80,
                overall_score=90,
                correctness_assessment="Assessment",
                is_incomplete_or_invalid=False,
                identified_bugs=[],
                time_complexity="O(N)",
                space_complexity="O(1)",
                complexity_explanation="Explanation",
            )

    def test_coding_submission_create_schema(self):
        sub = CodingSubmissionCreate(
            question_id="q123",
            language=CodingLanguage.PYTHON,
            code="def two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        diff = target - num\n        if diff in seen:\n            return [seen[diff], i]\n        seen[num] = i\n    return []",
        )
        self.assertEqual(sub.language, CodingLanguage.PYTHON)
        self.assertIn("def two_sum", sub.code)


if __name__ == "__main__":
    unittest.main()
