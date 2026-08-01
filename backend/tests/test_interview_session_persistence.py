"""Unit tests for Phase 6 Interview Session database persistence across turns."""

import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from beanie import PydanticObjectId

from app.models.interview import (
    DifficultyDecision,
    DifficultyLevel,
    InterviewQuestionModel,
    InterviewSession,
    QuestionCategory,
    SessionStatus,
)
from app.schemas.interview import (
    AdaptiveNextQuestionResponse,
    AnswerEvaluation,
    DifficultyAdjustment,
    DimensionScore,
    GeneratedQuestionList,
    IdealAnswerComparison,
    InterviewQuestion,
    InterviewSessionStartRequest,
    InterviewTurnSubmitRequest,
)
from app.services import interview_service


class FakeAIService:
    def __init__(self, responses: list[object]):
        self.responses = responses

    async def get_structured_response(self, **kwargs):
        if not self.responses:
            raise RuntimeError("No fake response left for AIService call")
        return self.responses.pop(0)


class TestInterviewSessionPersistence(unittest.TestCase):

    def test_start_session_persists_initial_question_pool(self):
        candidate_id = "507f1f77bcf86cd799439011"
        job_id = "507f1f77bcf86cd799439012"

        q1 = InterviewQuestion(
            question_text="Explain Python concurrency.",
            category=QuestionCategory.TECHNICAL,
            difficulty=DifficultyLevel.MEDIUM,
        )
        fake_gen = GeneratedQuestionList(questions=[q1])
        ai = FakeAIService([fake_gen])

        mock_job = SimpleNamespace(
            id=PydanticObjectId(job_id),
            title="Backend Engineer",
            description="Python FastAPI engineer role",
            model_dump=lambda **_: {"title": "Backend Engineer", "description": "Python FastAPI engineer role"},
        )

        with patch.object(InterviewSession, "get_pymongo_collection", return_value=MagicMock()), \
             patch.object(interview_service.job_repo, "get_by_id", AsyncMock(return_value=mock_job)), \
             patch.object(interview_service, "_get_candidate_profile_context", AsyncMock(return_value='{"name": "Alice"}')), \
             patch.object(interview_service.interview_repo, "create_session", AsyncMock(side_effect=lambda s: s)) as create_mock:

            res = asyncio.run(
                interview_service.start_interview_session(
                    candidate_id=candidate_id,
                    data=InterviewSessionStartRequest(job_id=job_id, initial_difficulty=DifficultyLevel.MEDIUM, total_questions=2),
                    ai_service=ai,
                )
            )

            self.assertEqual(create_mock.await_count, 1)
            created_session: InterviewSession = create_mock.await_args[0][0]
            self.assertEqual(created_session.status, SessionStatus.IN_PROGRESS)
            self.assertEqual(created_session.current_difficulty, DifficultyLevel.MEDIUM)
            self.assertEqual(len(created_session.question_pool), 1)
            self.assertEqual(res.current_question.question_text, "Explain Python concurrency.")

    def test_turn_submission_persists_evaluation_ideal_and_difficulty_adjustment(self):
        candidate_id = "507f1f77bcf86cd799439011"
        session_id = "507f1f77bcf86cd799439013"
        job_id = "507f1f77bcf86cd799439012"

        q1 = InterviewQuestionModel(
            question_text="What is FastAPI dependency injection?",
            category=QuestionCategory.TECHNICAL,
            difficulty=DifficultyLevel.MEDIUM,
        )

        existing_session = InterviewSession.model_construct(
            id=PydanticObjectId(session_id),
            candidate_id=PydanticObjectId(candidate_id),
            job_id=PydanticObjectId(job_id),
            initial_difficulty=DifficultyLevel.MEDIUM,
            current_difficulty=DifficultyLevel.MEDIUM,
            current_question_index=0,
            total_questions=2,
            status=SessionStatus.IN_PROGRESS,
            question_pool=[q1],
            turns=[],
            questions=[q1.question_text],
            answers=[],
        )

        eval_mock = AnswerEvaluation(
            technical_correctness=DimensionScore(score=9, justification="Spot on"),
            communication_clarity=DimensionScore(score=9, justification="Clear"),
            confidence=DimensionScore(score=8, justification="Confident"),
            grammar=DimensionScore(score=9, justification="Good"),
            completeness=DimensionScore(score=9, justification="Complete"),
            overall_turn_score=88,
            overall_feedback="Excellent response.",
        )
        ideal_mock = IdealAnswerComparison(
            ideal_answer="FastAPI relies on Depends to resolve dependencies...",
            key_strengths=["Identified Depends syntax"],
            missing_points=[],
            comparison_summary="Great answer",
        )
        adaptive_mock = AdaptiveNextQuestionResponse(
            difficulty_decision=DifficultyDecision.INCREASE,
            reasoning="Outstanding answer, increasing difficulty.",
            next_difficulty=DifficultyLevel.HARD,
            next_question=InterviewQuestion(
                question_text="How does ASGI differ from WSGI in high concurrency?",
                category=QuestionCategory.TECHNICAL,
                difficulty=DifficultyLevel.HARD,
            ),
        )

        ai = FakeAIService([eval_mock, ideal_mock, adaptive_mock])

        with patch.object(InterviewSession, "get_pymongo_collection", return_value=MagicMock()), \
             patch.object(interview_service.interview_repo, "get_session_by_id_and_candidate", AsyncMock(return_value=existing_session)), \
             patch.object(interview_service, "_get_job_context", AsyncMock(return_value={"title": "Backend Engineer"})), \
             patch.object(interview_service, "_get_candidate_profile_context", AsyncMock(return_value='{"name": "Alice"}')), \
             patch.object(interview_service.interview_repo, "save_session", AsyncMock(side_effect=lambda s: s)) as save_mock:

            res = asyncio.run(
                interview_service.submit_interview_turn(
                    candidate_id=candidate_id,
                    session_id=session_id,
                    data=InterviewTurnSubmitRequest(answer="FastAPI uses Depends for DI..."),
                    ai_service=ai,
                )
            )

            self.assertEqual(save_mock.await_count, 1)
            saved_session: InterviewSession = save_mock.await_args[0][0]

            self.assertEqual(len(saved_session.turns), 1)
            turn0 = saved_session.turns[0]
            self.assertEqual(turn0.candidate_answer, "FastAPI uses Depends for DI...")
            self.assertEqual(turn0.evaluation.overall_turn_score, 88)
            self.assertEqual(turn0.ideal_comparison.comparison_summary, "Great answer")
            self.assertIsNotNone(turn0.difficulty_adjustment)
            self.assertEqual(turn0.difficulty_adjustment.difficulty_decision, DifficultyDecision.INCREASE)

            self.assertEqual(saved_session.current_difficulty, DifficultyLevel.HARD)
            self.assertEqual(saved_session.current_question_index, 1)
            self.assertEqual(len(saved_session.question_pool), 2)
            self.assertEqual(res.next_question.question_text, "How does ASGI differ from WSGI in high concurrency?")

    def test_unauthorized_user_access_raises_not_found(self):
        owner_id = "507f1f77bcf86cd799439011"
        unauthorized_user_id = "507f1f77bcf86cd799439099"
        session_id = "507f1f77bcf86cd799439013"

        with patch.object(InterviewSession, "get_pymongo_collection", return_value=MagicMock()), \
             patch.object(interview_service.interview_repo, "get_session_by_id_and_candidate", AsyncMock(return_value=None)):

            from app.core.interview_exceptions import InterviewSessionNotFoundError

            with self.assertRaises(InterviewSessionNotFoundError):
                asyncio.run(
                    interview_service.get_session_details(unauthorized_user_id, session_id)
                )

            with self.assertRaises(InterviewSessionNotFoundError):
                asyncio.run(
                    interview_service.submit_interview_turn(
                        unauthorized_user_id, session_id, InterviewTurnSubmitRequest(answer="Unauthorized turn")
                    )
                )

    def test_submitting_turn_on_completed_or_abandoned_session_raises_error(self):
        candidate_id = "507f1f77bcf86cd799439011"
        session_id = "507f1f77bcf86cd799439013"

        completed_session = InterviewSession.model_construct(
            id=PydanticObjectId(session_id),
            candidate_id=PydanticObjectId(candidate_id),
            status=SessionStatus.COMPLETED,
        )

        abandoned_session = InterviewSession.model_construct(
            id=PydanticObjectId(session_id),
            candidate_id=PydanticObjectId(candidate_id),
            status=SessionStatus.ABANDONED,
        )

        from app.core.interview_exceptions import InterviewSessionCompletedError

        with patch.object(InterviewSession, "get_pymongo_collection", return_value=MagicMock()), \
             patch.object(interview_service.interview_repo, "get_session_by_id_and_candidate", AsyncMock(return_value=completed_session)):
            with self.assertRaises(InterviewSessionCompletedError):
                asyncio.run(
                    interview_service.submit_interview_turn(
                        candidate_id, session_id, InterviewTurnSubmitRequest(answer="Late turn")
                    )
                )

        with patch.object(InterviewSession, "get_pymongo_collection", return_value=MagicMock()), \
             patch.object(interview_service.interview_repo, "get_session_by_id_and_candidate", AsyncMock(return_value=abandoned_session)):
            with self.assertRaises(InterviewSessionCompletedError):
                asyncio.run(
                    interview_service.submit_interview_turn(
                        candidate_id, session_id, InterviewTurnSubmitRequest(answer="Abandoned turn")
                    )
                )

    def test_abandon_interview_session(self):
        candidate_id = "507f1f77bcf86cd799439011"
        session_id = "507f1f77bcf86cd799439013"

        session = InterviewSession.model_construct(
            id=PydanticObjectId(session_id),
            candidate_id=PydanticObjectId(candidate_id),
            status=SessionStatus.IN_PROGRESS,
            question_pool=[],
            turns=[],
            current_question_index=0,
            total_questions=3,
        )

        with patch.object(InterviewSession, "get_pymongo_collection", return_value=MagicMock()), \
             patch.object(interview_service.interview_repo, "get_session_by_id_and_candidate", AsyncMock(return_value=session)), \
             patch.object(interview_service.interview_repo, "save_session", AsyncMock(side_effect=lambda s: s)):

            res = asyncio.run(interview_service.abandon_interview_session(candidate_id, session_id))
            self.assertEqual(res.status, SessionStatus.ABANDONED)


if __name__ == "__main__":
    unittest.main()
