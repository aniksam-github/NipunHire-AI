"""Unit tests for Phase 7 Coding AI service logic using mocked AIService."""

import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from beanie import PydanticObjectId

from app.models.coding import CodingChallenge, CodingDifficulty, CodingLanguage, CodingSubmission
from app.schemas.coding import (
    CodingExample,
    CodingQuestionGenerated,
    CodingQuestionGenerateRequest,
    CodingReviewResult,
    CodingSubmissionCreate,
)
from app.services import coding_service


class FakeAIService:
    """Mock AIService providing pre-configured structured responses."""

    def __init__(self, responses: list[object]):
        self.responses = responses
        self.call_history: list[dict] = []

    async def get_structured_response(self, **kwargs):
        self.call_history.append(kwargs)
        if not self.responses:
            raise RuntimeError("No fake response remaining in queue")
        return self.responses.pop(0)


class TestCodingService(unittest.TestCase):

    def test_generate_coding_question(self):
        candidate_id = "507f1f77bcf86cd799439011"
        job_id = "507f1f77bcf86cd799439012"

        fake_gen = CodingQuestionGenerated(
            title="LRU Cache Implementation",
            problem_statement="Design a Least Recently Used (LRU) cache data structure...",
            input_output_format="Capacity: int, operations...",
            examples=[CodingExample(input="LRUCache(2)", output="null")],
            constraints=["1 <= capacity <= 3000"],
            difficulty=CodingDifficulty.MEDIUM,
            topics=["hash-table", "doubly-linked-list"],
            starter_code="class LRUCache:\n    def __init__(self, capacity: int):\n        pass",
        )
        ai = FakeAIService([fake_gen])

        mock_job = SimpleNamespace(
            id=PydanticObjectId(job_id),
            title="Systems Engineer",
            description="Python & C++ Backend role",
            model_dump=lambda **_: {
                "title": "Systems Engineer",
                "description": "Python & C++ Backend role",
                "required_skills": ["Python", "Algorithms"],
                "optional_skills": ["C++"],
            },
        )

        with patch.object(CodingChallenge, "get_pymongo_collection", return_value=MagicMock()), \
             patch.object(coding_service.job_repo, "get_by_id", AsyncMock(return_value=mock_job)), \
             patch.object(coding_service, "_get_candidate_profile_context", AsyncMock(return_value='{"skills": ["Python"]}')), \
             patch.object(coding_service.coding_repo, "create_challenge", AsyncMock(side_effect=lambda c: c)):

            res = asyncio.run(
                coding_service.generate_coding_question(
                    candidate_id=candidate_id,
                    data=CodingQuestionGenerateRequest(job_id=job_id, difficulty=CodingDifficulty.MEDIUM),
                    ai_service=ai,
                )
            )

            self.assertEqual(res.question.title, "LRU Cache Implementation")
            self.assertEqual(res.question.difficulty, CodingDifficulty.MEDIUM)
            self.assertIn("Generate a comprehensive, realistic coding question", ai.call_history[0].get("user_prompt", "") or "")

    def test_review_submitted_code_valid_solution(self):
        fake_review = CodingReviewResult(
            correctness_score=95,
            code_quality_score=90,
            overall_score=93,
            correctness_assessment="The code correctly implements two pointers to check palindromes.",
            is_incomplete_or_invalid=False,
            identified_bugs=[],
            time_complexity="O(N)",
            space_complexity="O(1)",
            complexity_explanation="Single pass with left and right pointers using O(1) space.",
            code_quality_observations=["Clean syntax and edge case checks"],
            optimization_suggestions=[],
        )
        ai = FakeAIService([fake_review])

        res = asyncio.run(
            coding_service.review_submitted_code(
                problem_title="Valid Palindrome",
                problem_statement="Check if string is palindrome",
                constraints=["1 <= s.length <= 10^5"],
                declared_language="python",
                submitted_code="def is_palindrome(s):\n    l, r = 0, len(s)-1\n    while l < r:\n        if s[l] != s[r]: return False\n        l += 1; r -= 1\n    return True",
                ai_service=ai,
            )
        )

        self.assertEqual(res.overall_score, 93)
        self.assertEqual(res.time_complexity, "O(N)")
        self.assertFalse(res.is_incomplete_or_invalid)
        self.assertIn("SECURITY & STATIC ANALYSIS DIRECTIVE", ai.call_history[0].get("user_prompt", "") or "")

    def test_review_submitted_code_flags_incomplete_syntax_error(self):
        fake_review = CodingReviewResult(
            correctness_score=10,
            code_quality_score=20,
            overall_score=13,
            correctness_assessment="Code snippet is incomplete and contains unclosed parentheses.",
            is_incomplete_or_invalid=True,
            identified_bugs=["Syntax error: unexpected EOF while parsing", "Unclosed loop statement"],
            time_complexity="N/A (Syntax Error)",
            space_complexity="N/A (Syntax Error)",
            complexity_explanation="Cannot determine asymptotic complexity due to syntax error.",
            code_quality_observations=["Incomplete code snippet submitted"],
            optimization_suggestions=["Fix syntax errors before submitting"],
        )
        ai = FakeAIService([fake_review])

        res = asyncio.run(
            coding_service.review_submitted_code(
                problem_title="Broken Snippet",
                problem_statement="Reverse a string",
                constraints=[],
                declared_language="python",
                submitted_code="def reverse_str(s:\n    for char in",
                ai_service=ai,
            )
        )

        self.assertTrue(res.is_incomplete_or_invalid)
        self.assertEqual(res.time_complexity, "N/A (Syntax Error)")
        self.assertIn("Syntax error", res.identified_bugs[0])


if __name__ == "__main__":
    unittest.main()
