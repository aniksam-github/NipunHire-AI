"""
Unit tests for AI Career Assistant Agent orchestration, multi-step tool chaining,
single-step execution, tool-call cap enforcement, failure resilience, and server-side ID locking.
"""

import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from beanie import PydanticObjectId

from app.models.agent_session import AgentSession
from app.schemas.agent import AgentChatRequest
from app.services.agent_service import AgentService, MAX_TOOL_CALLS_PER_TURN
from app.services.agent_tools import execute_tool


class AgentServiceTests(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.candidate_id = str(PydanticObjectId())
        self.agent_service = AgentService()
        self.patcher = patch.object(AgentSession, "get_pymongo_collection", return_value=MagicMock())
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    @patch("app.models.agent_session.AgentSession.save", new_callable=AsyncMock)
    @patch("app.services.agent_service.execute_tool")
    async def test_agent_multistep_tool_chaining(self, mock_execute_tool, mock_save):
        """Test multi-step tool chaining: Tool 1 (screening) -> Tool 2 (improvements) -> Final Answer."""
        # 1. Mock Tool Execution Returns
        mock_execute_tool.side_effect = [
            {"status": "success", "tool": "screen_and_analyze_resume", "data": {"strengths": ["Python expertise"]}},
            {"status": "success", "tool": "get_resume_improvement_suggestions", "data": {"rewrites": ["Updated impact bullets"]}},
        ]

        # 2. Mock OpenAI API Responses
        tc1 = MagicMock()
        tc1.id = "call_1"
        tc1.function.name = "screen_and_analyze_resume"
        tc1.function.arguments = "{}"
        resp1 = MagicMock()
        resp1.usage.prompt_tokens = 100
        resp1.usage.completion_tokens = 50
        resp1.choices = [MagicMock(message=MagicMock(content=None, tool_calls=[tc1]))]

        tc2 = MagicMock()
        tc2.id = "call_2"
        tc2.function.name = "get_resume_improvement_suggestions"
        tc2.function.arguments = "{}"
        resp2 = MagicMock()
        resp2.usage.prompt_tokens = 150
        resp2.usage.completion_tokens = 60
        resp2.choices = [MagicMock(message=MagicMock(content=None, tool_calls=[tc2]))]

        resp3 = MagicMock()
        resp3.usage.prompt_tokens = 200
        resp3.usage.completion_tokens = 80
        resp3.choices = [MagicMock(message=MagicMock(content="Here is a comprehensive summary based on your resume evaluation and improvements.", tool_calls=None))]

        mock_ai_service = MagicMock()
        mock_ai_service._model = "gpt-4o-mini"
        mock_ai_service.total_prompt_tokens = 0
        mock_ai_service.total_completion_tokens = 0
        mock_ai_service._client.chat.completions.create = AsyncMock(side_effect=[resp1, resp2, resp3])

        payload = AgentChatRequest(message="How can I improve my overall candidate profile for senior roles?")
        response = await self.agent_service.chat(
            candidate_id=self.candidate_id,
            payload=payload,
            ai_service=mock_ai_service,
        )

        self.assertIsNotNone(response.session_id)
        self.assertIn("comprehensive summary", response.answer)
        self.assertEqual(len(response.tool_calls_executed), 2)
        self.assertEqual(response.tool_calls_executed[0].tool_name, "screen_and_analyze_resume")
        self.assertEqual(response.tool_calls_executed[1].tool_name, "get_resume_improvement_suggestions")
        self.assertEqual(response.tool_call_count, 2)

    @patch("app.models.agent_session.AgentSession.save", new_callable=AsyncMock)
    async def test_agent_singlestep_scenario(self, mock_save):
        """Test single-step scenario where model answers directly without invoking tool calls."""
        resp = MagicMock()
        resp.usage.prompt_tokens = 50
        resp.usage.completion_tokens = 30
        resp.choices = [MagicMock(message=MagicMock(content="To use the STAR method on your resume, highlight Situation, Task, Action, Result.", tool_calls=None))]

        mock_ai_service = MagicMock()
        mock_ai_service._model = "gpt-4o-mini"
        mock_ai_service.total_prompt_tokens = 0
        mock_ai_service.total_completion_tokens = 0
        mock_ai_service._client.chat.completions.create = AsyncMock(return_value=resp)

        payload = AgentChatRequest(message="What is the STAR method for resumes?")
        response = await self.agent_service.chat(
            candidate_id=self.candidate_id,
            payload=payload,
            ai_service=mock_ai_service,
        )

        self.assertIn("STAR method", response.answer)
        self.assertEqual(len(response.tool_calls_executed), 0)
        self.assertEqual(response.tool_call_count, 0)

    @patch("app.models.agent_session.AgentSession.save", new_callable=AsyncMock)
    @patch("app.services.agent_service.execute_tool")
    async def test_agent_tool_execution_failure_resilience(self, mock_execute_tool, mock_save):
        """Test tool execution failure mid-conversation is caught, fed back as tool error, and loop continues."""
        mock_execute_tool.return_value = {
            "status": "error",
            "tool": "screen_and_analyze_resume",
            "error": "AI service timeout",
            "message": "Execution of screen_and_analyze_resume failed.",
        }

        tc = MagicMock()
        tc.id = "call_fail"
        tc.function.name = "screen_and_analyze_resume"
        tc.function.arguments = "{}"
        resp1 = MagicMock()
        resp1.usage.prompt_tokens = 100
        resp1.usage.completion_tokens = 20
        resp1.choices = [MagicMock(message=MagicMock(content=None, tool_calls=[tc]))]

        resp2 = MagicMock()
        resp2.usage.prompt_tokens = 120
        resp2.usage.completion_tokens = 40
        resp2.choices = [MagicMock(message=MagicMock(content="I encountered a temporary error reading your resume, but here are general tips.", tool_calls=None))]

        mock_ai_service = MagicMock()
        mock_ai_service._model = "gpt-4o-mini"
        mock_ai_service.total_prompt_tokens = 0
        mock_ai_service.total_completion_tokens = 0
        mock_ai_service._client.chat.completions.create = AsyncMock(side_effect=[resp1, resp2])

        payload = AgentChatRequest(message="Screen my resume please.")
        response = await self.agent_service.chat(
            candidate_id=self.candidate_id,
            payload=payload,
            ai_service=mock_ai_service,
        )

        self.assertIn("general tips", response.answer)
        self.assertEqual(len(response.tool_calls_executed), 1)
        self.assertEqual(response.tool_calls_executed[0].status, "error")
        self.assertEqual(response.tool_calls_executed[0].error_message, "AI service timeout")

    @patch("app.models.agent_session.AgentSession.save", new_callable=AsyncMock)
    @patch("app.services.agent_service.execute_tool")
    async def test_agent_tool_call_cap_enforcement(self, mock_execute_tool, mock_save):
        """Test hard cap limit (5) on tool calls per turn prevents runaway loops and returns graceful fallback."""
        mock_execute_tool.return_value = {"status": "success", "tool": "extract_skills_and_gaps", "data": {}}

        # Mock OpenAI repeatedly asking for tool calls indefinitely
        tc = MagicMock()
        tc.id = "call_loop"
        tc.function.name = "extract_skills_and_gaps"
        tc.function.arguments = "{}"
        resp_loop = MagicMock()
        resp_loop.usage.prompt_tokens = 50
        resp_loop.usage.completion_tokens = 10
        resp_loop.choices = [MagicMock(message=MagicMock(content=None, tool_calls=[tc]))]

        mock_ai_service = MagicMock()
        mock_ai_service._model = "gpt-4o-mini"
        mock_ai_service.total_prompt_tokens = 0
        mock_ai_service.total_completion_tokens = 0
        mock_ai_service._client.chat.completions.create = AsyncMock(return_value=resp_loop)

        payload = AgentChatRequest(message="Continuously extract skills")
        response = await self.agent_service.chat(
            candidate_id=self.candidate_id,
            payload=payload,
            ai_service=mock_ai_service,
        )

        self.assertEqual(response.tool_call_count, MAX_TOOL_CALLS_PER_TURN)
        self.assertIn("maximum step limit", response.answer)
        self.assertEqual(len(response.tool_calls_executed), MAX_TOOL_CALLS_PER_TURN)

    @patch("app.services.agent_tools.resume_screening_service.analyze_profile")
    @patch("app.services.agent_tools._resolve_candidate_profile")
    async def test_agent_server_side_id_injection(self, mock_resolve, mock_analyze):
        """Test server-side ID injection overrides hallucinated/model-supplied IDs."""
        mock_resume = MagicMock(id=PydanticObjectId())
        mock_profile = MagicMock()
        mock_resolve.return_value = (mock_resume, mock_profile)
        mock_analyze.return_value = MagicMock(model_dump=lambda mode: {"status": "ok"})

        # Model supplies fake/hallucinated arguments: resume_id="fake_999", candidate_id="fake_user"
        model_arguments = {"resume_id": "fake_999", "candidate_id": "fake_user"}

        result = await execute_tool(
            tool_name="screen_and_analyze_resume",
            arguments=model_arguments,
            candidate_id=self.candidate_id,
            request_resume_id=None,
        )

        self.assertEqual(result["status"], "success")
        # Confirms _resolve_candidate_profile was called with authenticated candidate_id, NOT fake_user
        mock_resolve.assert_called_once_with(self.candidate_id, None)


if __name__ == "__main__":
    unittest.main()
