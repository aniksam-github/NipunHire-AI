"""
Agentic AI Career Assistant Service — Multi-turn conversation loop, tool execution,
cap enforcement, tool logging, and session state persistence.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from beanie import PydanticObjectId

from app.ai.services.ai_service import AIService
from app.core.exceptions import AuthorizationError, EntityNotFoundError
from app.models.agent_session import AgentMessageModel, AgentSession, AgentToolExecutionLog
from app.schemas.agent import (
    AgentChatRequest,
    AgentChatResponse,
    AgentSessionResponse,
    AgentToolCallSummary,
)
from app.services.agent_tools import CAREER_ASSISTANT_TOOLS, execute_tool
from app.services.prompt_service import load_prompt

logger = logging.getLogger(__name__)

MAX_TOOL_CALLS_PER_TURN = 5


class AgentService:
    """Orchestrator for candidate-facing multi-turn tool-calling agentic sessions."""

    async def chat(
        self, candidate_id: str, payload: AgentChatRequest, ai_service: AIService | None = None
    ) -> AgentChatResponse:
        client = ai_service or AIService()

        # 1. Load or Create Session
        if payload.session_id:
            try:
                session = await AgentSession.get(PydanticObjectId(payload.session_id))
            except Exception:
                session = None
            if not session:
                raise EntityNotFoundError(entity="AgentSession", identifier=payload.session_id)
            if str(session.candidate_id) != candidate_id:
                raise AuthorizationError(detail="You can only access your own agent sessions.")
        else:
            session = AgentSession(
                candidate_id=PydanticObjectId(candidate_id),
                title=f"Session: {payload.message[:35]}",
                messages=[],
                tool_logs=[],
            )
            await session.save()

        # 2. Ensure System Prompt is initialized
        if not session.messages or session.messages[0].role != "system":
            system_prompt = load_prompt("career_assistant_agent")
            session.messages.insert(0, AgentMessageModel(role="system", content=system_prompt))

        # 3. Add Candidate User Message
        user_msg = AgentMessageModel(role="user", content=payload.message)
        session.messages.append(user_msg)

        # 4. Construct OpenAI Message Trajectory
        openai_messages: list[dict[str, Any]] = []
        for m in session.messages:
            msg_dict: dict[str, Any] = {"role": m.role}
            if m.content is not None:
                msg_dict["content"] = m.content
            if m.name is not None:
                msg_dict["name"] = m.name
            if m.tool_call_id is not None:
                msg_dict["tool_call_id"] = m.tool_call_id
            if m.tool_calls is not None:
                msg_dict["tool_calls"] = m.tool_calls
            openai_messages.append(msg_dict)

        # 5. Multi-Turn Tool Loop
        tool_calls_count = 0
        turn_tool_summaries: list[AgentToolCallSummary] = []
        final_answer: str | None = None

        while tool_calls_count < MAX_TOOL_CALLS_PER_TURN:
            response = await client._client.chat.completions.create(
                model=client._model,
                messages=openai_messages,
                tools=CAREER_ASSISTANT_TOOLS,
                tool_choice="auto",
                temperature=0.4,
            )

            usage = response.usage
            if usage:
                client.total_prompt_tokens += usage.prompt_tokens or 0
                client.total_completion_tokens += usage.completion_tokens or 0

            choice = response.choices[0]
            response_msg = choice.message

            # Format Assistant Message for trajectory
            assistant_dict: dict[str, Any] = {"role": "assistant"}
            if response_msg.content:
                assistant_dict["content"] = response_msg.content
            if response_msg.tool_calls:
                assistant_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in response_msg.tool_calls
                ]

            openai_messages.append(assistant_dict)
            session.messages.append(
                AgentMessageModel(
                    role="assistant",
                    content=response_msg.content,
                    tool_calls=assistant_dict.get("tool_calls"),
                )
            )

            # Check if model produced a final text answer without tool calls
            if not response_msg.tool_calls:
                final_answer = response_msg.content or "I have processed your request."
                break

            # Model requested tool call(s)
            for tool_call in response_msg.tool_calls:
                if tool_calls_count >= MAX_TOOL_CALLS_PER_TURN:
                    logger.warning("Tool call cap (%d) reached for candidate %s", MAX_TOOL_CALLS_PER_TURN, candidate_id)
                    break

                tool_calls_count += 1
                func_name = tool_call.function.name
                try:
                    args_dict = json.loads(tool_call.function.arguments or "{}")
                except Exception:
                    args_dict = {}

                # Execute Tool with Server-Side ID Enforcement & Error Catching
                tool_result = await execute_tool(
                    tool_name=func_name,
                    arguments=args_dict,
                    candidate_id=candidate_id,
                    request_resume_id=payload.resume_id,
                    request_job_id=payload.job_id,
                    ai_service=client,
                )

                # Build Tool Output Message for trajectory
                tool_msg_dict = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": json.dumps(tool_result),
                }
                openai_messages.append(tool_msg_dict)
                session.messages.append(
                    AgentMessageModel(
                        role="tool",
                        tool_call_id=tool_call.id,
                        name=func_name,
                        content=json.dumps(tool_result),
                    )
                )

                # Log Tool Execution to Session
                log_entry = AgentToolExecutionLog(
                    tool_name=func_name,
                    arguments=args_dict,
                    status=tool_result.get("status", "success"),
                    result=tool_result.get("data"),
                    error_message=tool_result.get("error"),
                    step_number=len(session.tool_logs) + 1,
                )
                session.tool_logs.append(log_entry)
                turn_tool_summaries.append(
                    AgentToolCallSummary(
                        tool_name=func_name,
                        arguments=args_dict,
                        status=tool_result.get("status", "success"),
                        error_message=tool_result.get("error"),
                        timestamp=log_entry.timestamp,
                    )
                )

        # 6. Graceful Cap Failure Check
        if final_answer is None:
            final_answer = (
                "The assistant reached the maximum step limit while analyzing your request. "
                "Here is a summary of tool executions completed so far: "
                + ", ".join([f"{t.tool_name} ({t.status})" for t in turn_tool_summaries])
            )
            fallback_msg = AgentMessageModel(role="assistant", content=final_answer)
            session.messages.append(fallback_msg)

        # 7. Persist Session State
        session.updated_at = datetime.now(timezone.utc)
        await session.save()

        return AgentChatResponse(
            session_id=str(session.id),
            answer=final_answer,
            tool_calls_executed=turn_tool_summaries,
            tool_call_count=tool_calls_count,
            created_at=session.created_at,
        )

    async def get_session(self, session_id: str, candidate_id: str) -> AgentSessionResponse:
        try:
            session = await AgentSession.get(PydanticObjectId(session_id))
        except Exception:
            session = None
        if not session:
            raise EntityNotFoundError(entity="AgentSession", identifier=session_id)
        if str(session.candidate_id) != candidate_id:
            raise AuthorizationError(detail="You can only access your own agent sessions.")

        return AgentSessionResponse(
            session_id=str(session.id),
            candidate_id=str(session.candidate_id),
            title=session.title,
            messages=[m.model_dump(mode="json") for m in session.messages],
            tool_logs=[
                AgentToolCallSummary(
                    tool_name=log.tool_name,
                    arguments=log.arguments,
                    status=log.status,
                    error_message=log.error_message,
                    timestamp=log.timestamp,
                )
                for log in session.tool_logs
            ],
            created_at=session.created_at,
            updated_at=session.updated_at,
        )

    async def list_sessions(self, candidate_id: str) -> list[AgentSessionResponse]:
        sessions = (
            await AgentSession.find(AgentSession.candidate_id == PydanticObjectId(candidate_id))
            .sort("-updated_at")
            .to_list()
        )
        return [
            AgentSessionResponse(
                session_id=str(s.id),
                candidate_id=str(s.candidate_id),
                title=s.title,
                messages=[m.model_dump(mode="json") for m in s.messages],
                tool_logs=[
                    AgentToolCallSummary(
                        tool_name=log.tool_name,
                        arguments=log.arguments,
                        status=log.status,
                        error_message=log.error_message,
                        timestamp=log.timestamp,
                    )
                    for log in s.tool_logs
                ],
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in sessions
        ]

    async def delete_session(self, session_id: str, candidate_id: str) -> None:
        try:
            session = await AgentSession.get(PydanticObjectId(session_id))
        except Exception:
            session = None
        if not session:
            raise EntityNotFoundError(entity="AgentSession", identifier=session_id)
        if str(session.candidate_id) != candidate_id:
            raise AuthorizationError(detail="You can only delete your own agent sessions.")
        await session.delete()


# Singleton Agent Service Instance
agent_service = AgentService()
