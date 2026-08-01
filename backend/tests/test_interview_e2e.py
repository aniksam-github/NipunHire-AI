"""End-to-end multi-turn adaptive interview simulation tests with mocked AI responses."""

import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from beanie import PydanticObjectId

from app.models.interview import (
    DifficultyDecision,
    DifficultyLevel,
    InterviewSession,
    QuestionCategory,
    SessionStatus,
)
from app.schemas.interview import (
    AdaptiveNextQuestionResponse,
    AnswerEvaluation,
    DimensionScore,
    GeneratedQuestionList,
    HiringRecommendation,
    IdealAnswerComparison,
    InterviewQuestion,
    InterviewReport,
    InterviewSessionStartRequest,
    InterviewTurnSubmitRequest,
)
from app.services import interview_service


class MultiTurnFakeAIService:
    """Mock AI Service queueing pre-programmed outputs for multi-turn execution."""

    def __init__(self, responses: list[object]):
        self.responses = responses

    async def get_structured_response(self, **kwargs):
        if not self.responses:
            raise RuntimeError("No fake response remaining in queue")
        return self.responses.pop(0)


class TestInterviewE2E(unittest.TestCase):

    def test_full_multi_turn_session_simulation_e2e(self):
        candidate_id = "507f1f77bcf86cd799439011"
        job_id = "507f1f77bcf86cd799439012"
        session_id = "507f1f77bcf86cd799439013"

        # 1. Module 1 AI Output (Initial Questions)
        initial_q1 = InterviewQuestion(
            question_text="Q1: Explain REST API principles.",
            category=QuestionCategory.TECHNICAL,
            difficulty=DifficultyLevel.MEDIUM,
        )
        mod1_gen = GeneratedQuestionList(questions=[initial_q1])

        # 2. Turn 1 AI Outputs (Eval, Ideal, Adaptive Next Q)
        eval_turn1 = AnswerEvaluation(
            technical_correctness=DimensionScore(score=9, justification="Correct principles"),
            communication_clarity=DimensionScore(score=9, justification="Structured"),
            confidence=DimensionScore(score=8, justification="Confident"),
            grammar=DimensionScore(score=9, justification="Good syntax"),
            completeness=DimensionScore(score=8, justification="Complete"),
            overall_turn_score=86,
            overall_feedback="Great turn 1 answer.",
        )
        ideal_turn1 = IdealAnswerComparison(
            ideal_answer="Ideal explanation of REST statelessness and uniform interface...",
            key_strengths=["Mentioned statelessness"],
            missing_points=["Omitted HATEOAS"],
            comparison_summary="Strong REST basics.",
        )
        next_q2 = InterviewQuestion(
            question_text="Q2: How do you handle distributed transactions across microservices?",
            category=QuestionCategory.TECHNICAL,
            difficulty=DifficultyLevel.HARD,
        )
        adaptive_turn1 = AdaptiveNextQuestionResponse(
            difficulty_decision=DifficultyDecision.INCREASE,
            reasoning="Candidate mastered medium question, advancing to hard question.",
            next_difficulty=DifficultyLevel.HARD,
            next_question=next_q2,
        )

        # 3. Turn 2 AI Outputs (Eval, Ideal - last turn so no adaptive call)
        eval_turn2 = AnswerEvaluation(
            technical_correctness=DimensionScore(score=8, justification="Explained Saga pattern well"),
            communication_clarity=DimensionScore(score=8, justification="Good explanation"),
            confidence=DimensionScore(score=8, justification="Good confidence"),
            grammar=DimensionScore(score=9, justification="Clear language"),
            completeness=DimensionScore(score=8, justification="Solid coverage"),
            overall_turn_score=82,
            overall_feedback="Well handled hard question.",
        )
        ideal_turn2 = IdealAnswerComparison(
            ideal_answer="Ideal explanation of Saga pattern and 2PC trade-offs...",
            key_strengths=["Detail on Saga orchestration vs choreography"],
            missing_points=["Could mention idempotent handlers"],
            comparison_summary="Good distributed systems understanding.",
        )

        # 4. Module 5 AI Output (Final Report)
        final_report = InterviewReport(
            overall_score=84,
            strengths=["REST fundamentals", "Microservice transaction patterns"],
            weaknesses=["Could include edge-case operational trade-offs"],
            hiring_recommendation=HiringRecommendation.HIRE,
            summary_justification="Candidate passed all difficulty calibration levels cleanly.",
            category_breakdown={
                "technical_correctness": 8.5,
                "communication_clarity": 8.5,
                "confidence": 8.0,
                "grammar": 9.0,
                "completeness": 8.0,
            },
        )

        # Pre-queue all expected AI responses
        ai = MultiTurnFakeAIService([
            mod1_gen,
            eval_turn1,
            ideal_turn1,
            adaptive_turn1,
            eval_turn2,
            ideal_turn2,
            final_report,
        ])

        mock_job = SimpleNamespace(
            id=PydanticObjectId(job_id),
            title="Senior Backend Engineer",
            description="Microservices and REST role",
            model_dump=lambda **_: {"title": "Senior Backend Engineer", "description": "Microservices and REST role"},
        )

        db_session_store: dict[str, InterviewSession] = {}

        async def fake_create_session(s: InterviewSession) -> InterviewSession:
            s.id = PydanticObjectId(session_id)
            db_session_store[str(s.id)] = s
            return s

        async def fake_get_session(s_id: str, c_id: str) -> InterviewSession | None:
            return db_session_store.get(s_id)

        async def fake_save_session(s: InterviewSession) -> InterviewSession:
            db_session_store[str(s.id)] = s
            return s

        with patch.object(InterviewSession, "get_pymongo_collection", return_value=MagicMock()), \
             patch.object(interview_service.job_repo, "get_by_id", AsyncMock(return_value=mock_job)), \
             patch.object(interview_service, "_get_candidate_profile_context", AsyncMock(return_value='{"name": "Alice"}')), \
             patch.object(interview_service.interview_repo, "create_session", AsyncMock(side_effect=fake_create_session)), \
             patch.object(interview_service.interview_repo, "get_session_by_id_and_candidate", AsyncMock(side_effect=fake_get_session)), \
             patch.object(interview_service.interview_repo, "save_session", AsyncMock(side_effect=fake_save_session)):

            # --- STEP 1: START INTERVIEW SESSION ---
            start_res = asyncio.run(
                interview_service.start_interview_session(
                    candidate_id=candidate_id,
                    data=InterviewSessionStartRequest(job_id=job_id, initial_difficulty=DifficultyLevel.MEDIUM, total_questions=2),
                    ai_service=ai,
                )
            )
            self.assertEqual(start_res.session_id, session_id)
            self.assertEqual(start_res.current_question.question_text, "Q1: Explain REST API principles.")
            self.assertEqual(start_res.current_difficulty, DifficultyLevel.MEDIUM)

            # --- STEP 2: TURN 1 SUBMISSION & ADAPTIVE DIFFICULTY INCREASE ---
            turn1_res = asyncio.run(
                interview_service.submit_interview_turn(
                    candidate_id=candidate_id,
                    session_id=session_id,
                    data=InterviewTurnSubmitRequest(answer="REST APIs use HTTP verbs and are stateless..."),
                    ai_service=ai,
                )
            )
            self.assertEqual(turn1_res.turn_index, 0)
            self.assertEqual(turn1_res.evaluation.overall_turn_score, 86)
            self.assertFalse(turn1_res.session_completed)
            self.assertEqual(turn1_res.current_difficulty, DifficultyLevel.HARD)
            self.assertEqual(turn1_res.next_question.question_text, "Q2: How do you handle distributed transactions across microservices?")

            # Verify persisted DB state after turn 1
            session_state1 = db_session_store[session_id]
            self.assertEqual(len(session_state1.turns), 1)
            self.assertEqual(session_state1.current_question_index, 1)

            # --- STEP 3: TURN 2 SUBMISSION (FINAL TURN) ---
            turn2_res = asyncio.run(
                interview_service.submit_interview_turn(
                    candidate_id=candidate_id,
                    session_id=session_id,
                    data=InterviewTurnSubmitRequest(answer="We can use Saga pattern with compensating transactions..."),
                    ai_service=ai,
                )
            )
            self.assertEqual(turn2_res.turn_index, 1)
            self.assertEqual(turn2_res.evaluation.overall_turn_score, 82)
            self.assertTrue(turn2_res.session_completed)
            self.assertIsNone(turn2_res.next_question)

            # Verify persisted DB state after turn 2
            session_state2 = db_session_store[session_id]
            self.assertEqual(len(session_state2.turns), 2)
            self.assertEqual(session_state2.status, SessionStatus.READY_TO_COMPLETE)

            # --- STEP 4: GENERATE FINAL INTERVIEW REPORT ---
            report_res = asyncio.run(
                interview_service.generate_final_report(
                    candidate_id=candidate_id,
                    session_id=session_id,
                    ai_service=ai,
                )
            )
            self.assertEqual(report_res.report.overall_score, 84)
            self.assertEqual(report_res.report.hiring_recommendation, HiringRecommendation.HIRE)
            self.assertEqual(len(report_res.report.strengths), 2)

            # Final check on DB object state
            final_session_state = db_session_store[session_id]
            self.assertEqual(final_session_state.status, SessionStatus.COMPLETED)
            self.assertIsNotNone(final_session_state.final_report)
            self.assertEqual(final_session_state.final_report.overall_score, 84)


if __name__ == "__main__":
    unittest.main()
