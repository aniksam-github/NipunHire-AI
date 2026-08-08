"""
Agentic AI Career Assistant API Router — multi-turn chat, session persistence, and audit log endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.core.exceptions import AuthorizationError, EntityNotFoundError
from app.models.user import User
from app.schemas.agent import AgentChatRequest, AgentChatResponse, AgentSessionResponse
from app.services.agent_service import agent_service

router = APIRouter(prefix="/agent", tags=["AI Career Assistant Agent"])


@router.post(
    "/chat",
    response_model=AgentChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with the autonomous AI Career Assistant Agent",
)
async def chat_with_agent(
    payload: AgentChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Candidate-facing agentic chat turn. Automatically chains underlying AI tool calls
    (screening, skill extraction, ATS optimization, career coaching) based on context.
    """
    try:
        return await agent_service.chat(
            candidate_id=str(current_user.id),
            payload=payload,
        )
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.detail) from exc


@router.get(
    "/sessions",
    response_model=list[AgentSessionResponse],
    status_code=status.HTTP_200_OK,
    summary="List all agent chat sessions for the authenticated candidate",
)
async def list_agent_sessions(
    current_user: User = Depends(get_current_user),
):
    return await agent_service.list_sessions(candidate_id=str(current_user.id))


@router.get(
    "/sessions/{session_id}",
    response_model=AgentSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get detailed history and tool execution logs for an agent session",
)
async def get_agent_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    try:
        return await agent_service.get_session(
            session_id=session_id,
            candidate_id=str(current_user.id),
        )
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.detail) from exc


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an agent chat session",
)
async def delete_agent_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    try:
        await agent_service.delete_session(
            session_id=session_id,
            candidate_id=str(current_user.id),
        )
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.detail) from exc
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.detail) from exc
