"""Authorization tests for Phase 7 Coding AI endpoints and service logic."""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from beanie import PydanticObjectId

from app.core.coding_exceptions import CodingSubmissionNotFoundError
from app.models.coding import CodingDifficulty, CodingLanguage, CodingReviewModel, CodingSubmission
from app.services import coding_service


class TestCodingAuthorization(unittest.TestCase):

    def test_unauthorized_candidate_cannot_access_other_users_submission(self):
        owner_candidate_id = "507f1f77bcf86cd799439011"
        unauthorized_candidate_id = "507f1f77bcf86cd799439099"
        submission_id = "507f1f77bcf86cd799439055"

        with patch.object(CodingSubmission, "get_pymongo_collection", return_value=MagicMock()), \
             patch.object(coding_service.coding_repo, "get_submission_by_id_and_candidate", AsyncMock(return_value=None)):

            # Unauthorized candidate attempting to access User A's submission MUST raise NotFoundError (404)
            with self.assertRaises(CodingSubmissionNotFoundError):
                asyncio.run(
                    coding_service.get_consolidated_feedback(
                        candidate_id=unauthorized_candidate_id,
                        submission_id=submission_id,
                    )
                )

    def test_authorized_owner_can_access_own_submission(self):
        owner_candidate_id = "507f1f77bcf86cd799439011"
        submission_id = "507f1f77bcf86cd799439055"

        mock_review = CodingReviewModel(
            correctness_score=92,
            code_quality_score=88,
            overall_score=90,
            correctness_assessment="Correct implementation.",
            is_incomplete_or_invalid=False,
            identified_bugs=[],
            time_complexity="O(N)",
            space_complexity="O(1)",
            complexity_explanation="Linear execution",
        )

        mock_submission = CodingSubmission.model_construct(
            id=PydanticObjectId(submission_id),
            candidate_id=PydanticObjectId(owner_candidate_id),
            question_id="q101",
            question_title="Reverse Array",
            language=CodingLanguage.PYTHON,
            difficulty=CodingDifficulty.EASY,
            code="def rev(arr): return arr[::-1]",
            review=mock_review,
        )

        with patch.object(CodingSubmission, "get_pymongo_collection", return_value=MagicMock()), \
             patch.object(coding_service.coding_repo, "get_submission_by_id_and_candidate", AsyncMock(return_value=mock_submission)), \
             patch.object(coding_service.coding_repo, "get_challenge_by_id", AsyncMock(return_value=None)):

            response = asyncio.run(
                coding_service.get_consolidated_feedback(
                    candidate_id=owner_candidate_id,
                    submission_id=submission_id,
                )
            )

            self.assertEqual(response.submission_id, submission_id)
            self.assertEqual(response.candidate_id, owner_candidate_id)
            self.assertEqual(response.review.overall_score, 90)


if __name__ == "__main__":
    unittest.main()
