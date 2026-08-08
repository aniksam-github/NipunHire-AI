"""
Event-Driven Architecture (EDA) Engine.

Provides asynchronous event publishing, subscriber registration, and non-blocking
background event processing across NipunHire AI services.
"""

import asyncio
import time
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class Event:
    event_type: str
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)


EventHandler = Callable[[Event], Coroutine[Any, Any, None]]


class EventBus:
    """
    Asynchronous in-memory Event Bus & Pub/Sub broker.
    Decouples event producers from background processors (Elasticsearch indexing,
    audit trail logging, AI background jobs).
    """

    def __init__(self):
        self._subscribers: Dict[str, List[EventHandler]] = {}

    def clear(self) -> None:
        """Reset subscribers (used in unit testing)."""
        self._subscribers.clear()

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Register an async handler function for a specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)
            logger.info(f"Subscribed handler '{handler.__name__}' to event '{event_type}'")

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Unregister an async handler function."""
        if event_type in self._subscribers and handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    async def publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Publish an event to all registered subscribers.
        Executes subscribers asynchronously in non-blocking background tasks.
        """
        event = Event(event_type=event_type, payload=payload)
        handlers = self._subscribers.get(event_type, [])

        if not handlers:
            logger.debug(f"No subscribers registered for event '{event_type}'")
            return

        logger.info(f"Publishing event '{event_type}' to {len(handlers)} subscriber(s)")

        for handler in handlers:
            # Create a non-blocking background task for each subscriber
            asyncio.create_task(self._safe_execute(handler, event))

    async def _safe_execute(self, handler: EventHandler, event: Event) -> None:
        """Execute subscriber with error handling to prevent consumer crashes."""
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Error executing event handler '{handler.__name__}' for event '{event.event_type}': {e}", exc_info=True)


# Global Singleton Event Bus Instance
event_bus = EventBus()


# ---- Built-in Event Handlers (Subscribers) ----

async def handle_resume_uploaded(event: Event) -> None:
    """Async Subscriber: Auto-indexes resume text in Elasticsearch & logs audit trail."""
    payload = event.payload
    candidate_id = payload.get("candidate_id")
    candidate_name = payload.get("candidate_name", "Unknown Candidate")
    headline = payload.get("headline", "")
    resume_text = payload.get("resume_text", "")
    skills = payload.get("skills", [])

    logger.info(f"[EDA Event Handler] Processing 'resume.uploaded' for candidate {candidate_id}")

    # 1. Asynchronously index in Elasticsearch
    from app.db.elasticsearch import index_candidate_resume
    await index_candidate_resume(
        candidate_id=candidate_id,
        candidate_name=candidate_name,
        headline=headline,
        resume_text=resume_text,
        skills=skills
    )

    # 2. Asynchronously record Audit Log
    from app.services.audit_service import audit_service
    await audit_service.log_event(
        action="RESUME_UPLOADED_EVENT_PROCESSED",
        actor_id=candidate_id or "system",
        resource="resume",
        resource_id=candidate_id,
        details={"event_timestamp": event.timestamp, "skills_count": len(skills)}
    )


async def handle_interview_completed(event: Event) -> None:
    """Async Subscriber: Logs audit record on interview completion."""
    payload = event.payload
    session_id = payload.get("session_id")
    candidate_id = payload.get("candidate_id")
    score = payload.get("overall_score", 0.0)

    logger.info(f"[EDA Event Handler] Processing 'interview.completed' for session {session_id}")

    from app.services.audit_service import audit_service
    await audit_service.log_event(
        action="INTERVIEW_COMPLETED_EVENT_PROCESSED",
        actor_id=candidate_id or "system",
        resource="interview_session",
        resource_id=session_id,
        details={"overall_score": score, "completed_at": event.timestamp}
    )


def register_default_subscribers() -> None:
    """Register all default EDA subscribers on application startup."""
    event_bus.subscribe("resume.uploaded", handle_resume_uploaded)
    event_bus.subscribe("interview.completed", handle_interview_completed)
