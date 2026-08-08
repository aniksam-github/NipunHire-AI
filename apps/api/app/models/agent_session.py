"""Persistent multi-turn AI Career Assistant sessions and tool execution logs."""

from datetime import datetime, timezone
from typing import Any

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class AgentMessageModel(BaseModel):
    """Single message in the candidate-agent conversation trajectory."""

    role: str  # "system", "user", "assistant", "tool"
    content: str | None = None
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[dict[str, Any]] | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentToolExecutionLog(BaseModel):
    """Audit log entry for every tool call executed during an agent turn."""

    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    status: str = "success"  # "success" | "error"
    result: Any = None
    error_message: str | None = None
    step_number: int = 1
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentSession(Document):
    """Multi-turn session document stored in MongoDB."""

    candidate_id: PydanticObjectId
    title: str = Field(default="AI Career Assistant Session")
    messages: list[AgentMessageModel] = Field(default_factory=list)
    tool_logs: list[AgentToolExecutionLog] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "agent_sessions"
        indexes = ["candidate_id", [("updated_at", -1)]]
