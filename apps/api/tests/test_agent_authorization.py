"""
Authorization & Session Persistence Integration Tests for AI Career Assistant Agent.
Verifies multi-turn context retention and strict cross-candidate security isolation.
"""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from beanie import PydanticObjectId

from app.core.exceptions import AuthorizationError
from app.models.agent_session import AgentMessageModel, AgentSession
from app.schemas.agent import AgentChatRequest
from app.services.agent_service import AgentService


class AgentAuthorizationTests(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.candidate_a_id = str(PydanticObjectId())
        self.candidate_b_id = str(PydanticObjectId())
        self.agent_service = AgentService()
        self.patcher = patch.object(AgentSession, "get_pymongo_collection", return_value=MagicMock())
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    @patch("app.models.agent_session.AgentSession.save", new_callable=AsyncMock)
    @patch("app.models.agent_session.AgentSession.get")
    async def test_agent_session_persistence_multiturn(self, mock_session_get, mock_save):
        """Test candidate multi-turn conversation retains context across separate requests."""
        session_id = PydanticObjectId()
        existing_session = AgentSession(
            id=session_id,
            candidate_id=PydanticObjectId(self.candidate_a_id),
            title="Session 1",
            messages=[
                AgentMessageModel(role="system", content="System Prompt"),
                AgentMessageModel(role="user", content="Turn 1 Question"),
                AgentMessageModel(role="assistant", content="Turn 1 Answer"),
            ],
            tool_logs=[],
        )
        mock_session_get.return_value = existing_session

        # Mock OpenAI API for turn 2
        resp = MagicMock()
        resp.usage.prompt_tokens = 80
        resp.usage.completion_tokens = 40
        resp.choices = [MagicMock(message=MagicMock(content="Turn 2 Follow-up Answer", tool_calls=None))]

        mock_ai_service = MagicMock()
        mock_ai_service._model = "gpt-4o-mini"
        mock_ai_service.total_prompt_tokens = 0
        mock_ai_service.total_completion_tokens = 0
        mock_ai_service._client.chat.completions.create = AsyncMock(return_value=resp)

        payload = AgentChatRequest(message="Can you elaborate on Turn 1?", session_id=str(session_id))
        response = await self.agent_service.chat(
            candidate_id=self.candidate_a_id,
            payload=payload,
            ai_service=mock_ai_service,
        )

        self.assertEqual(response.session_id, str(session_id))
        self.assertEqual(response.answer, "Turn 2 Follow-up Answer")
        # Trajectory now contains system + turn 1 user + turn 1 assistant + turn 2 user + turn 2 assistant
        self.assertEqual(len(existing_session.messages), 5)
        self.assertEqual(existing_session.messages[-1].content, "Turn 2 Follow-up Answer")

    @patch("app.models.agent_session.AgentSession.get")
    async def test_agent_authorization_isolation_chat(self, mock_session_get):
        """Test Candidate B attempting to access Candidate A's session via chat returns 403 AuthorizationError."""
        session_id = PydanticObjectId()
        candidate_a_session = AgentSession(
            id=session_id,
            candidate_id=PydanticObjectId(self.candidate_a_id),
            title="Candidate A Session",
            messages=[],
            tool_logs=[],
        )
        mock_session_get.return_value = candidate_a_session

        payload = AgentChatRequest(message="Show me Candidate A's data", session_id=str(session_id))

        with self.assertRaises(AuthorizationError):
            await self.agent_service.chat(
                candidate_id=self.candidate_b_id,  # Unauthorized candidate B
                payload=payload,
            )

    @patch("app.models.agent_session.AgentSession.get")
    async def test_agent_authorization_isolation_get_session(self, mock_session_get):
        """Test Candidate B attempting to view Candidate A's session history returns 403 AuthorizationError."""
        session_id = PydanticObjectId()
        candidate_a_session = AgentSession(
            id=session_id,
            candidate_id=PydanticObjectId(self.candidate_a_id),
            title="Candidate A Private Session",
            messages=[],
            tool_logs=[],
        )
        mock_session_get.return_value = candidate_a_session

        with self.assertRaises(AuthorizationError):
            await self.agent_service.get_session(
                session_id=str(session_id),
                candidate_id=self.candidate_b_id,  # Unauthorized candidate B
            )

    @patch("app.models.agent_session.AgentSession.get")
    async def test_agent_authorization_isolation_delete_session(self, mock_session_get):
        """Test Candidate B attempting to delete Candidate A's session returns 403 AuthorizationError."""
        session_id = PydanticObjectId()
        candidate_a_session = AgentSession(
            id=session_id,
            candidate_id=PydanticObjectId(self.candidate_a_id),
            title="Candidate A Session",
            messages=[],
            tool_logs=[],
        )
        mock_session_get.return_value = candidate_a_session

        with self.assertRaises(AuthorizationError):
            await self.agent_service.delete_session(
                session_id=str(session_id),
                candidate_id=self.candidate_b_id,  # Unauthorized candidate B
            )


if __name__ == "__main__":
    unittest.main()
