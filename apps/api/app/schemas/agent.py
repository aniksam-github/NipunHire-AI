"""Schemas for the AI Career Assistant Agentic Orchestration Layer."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    """Payload for starting or continuing an agentic career assistant session."""

    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = Field(default=None, description="Optional existing session ID for multi-turn conversation.")
    resume_id: str | None = Field(default=None, description="Optional target resume ID (validated server-side).")
    job_id: str | None = Field(default=None, description="Optional target job ID (validated server-side).")


class AgentToolCallSummary(BaseModel):
    """Summary of a tool execution for client feedback and API responses."""

    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    status: str = "success"  # "success" | "error"
    error_message: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentChatResponse(BaseModel):
    """Response returned after processing a candidate conversation turn."""

    session_id: str
    answer: str
    tool_calls_executed: list[AgentToolCallSummary] = Field(default_factory=list)
    tool_call_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentSessionResponse(BaseModel):
    """Full detail of a persistent career assistant session."""

    session_id: str
    candidate_id: str
    title: str
    messages: list[dict[str, Any]] = Field(default_factory=list)
    tool_logs: list[AgentToolCallSummary] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
