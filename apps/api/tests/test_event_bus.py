"""
Unit tests for EventBus, Event dataclass, and EDA asynchronous subscriber dispatching.
"""

import asyncio
import pytest
from app.core.events import EventBus, Event, handle_resume_uploaded, handle_interview_completed


@pytest.fixture
def clean_event_bus():
    bus = EventBus()
    bus.clear()
    yield bus
    bus.clear()


@pytest.mark.asyncio
async def test_event_bus_subscribe_and_publish(clean_event_bus):
    bus = clean_event_bus
    received_events = []

    async def mock_handler(event: Event):
        received_events.append(event)

    bus.subscribe("test.event", mock_handler)
    await bus.publish("test.event", {"key": "value"})

    # Allow asyncio background tasks to process
    await asyncio.sleep(0.05)

    assert len(received_events) == 1
    assert received_events[0].event_type == "test.event"
    assert received_events[0].payload == {"key": "value"}


@pytest.mark.asyncio
async def test_event_bus_multiple_subscribers(clean_event_bus):
    bus = clean_event_bus
    call_counts = {"h1": 0, "h2": 0}

    async def h1(event: Event):
        call_counts["h1"] += 1

    async def h2(event: Event):
        call_counts["h2"] += 1

    bus.subscribe("candidate.screened", h1)
    bus.subscribe("candidate.screened", h2)

    await bus.publish("candidate.screened", {"candidate_id": "cand_001"})
    await asyncio.sleep(0.05)

    assert call_counts["h1"] == 1
    assert call_counts["h2"] == 1


@pytest.mark.asyncio
async def test_event_bus_fault_tolerance(clean_event_bus):
    bus = clean_event_bus
    succ_calls = []

    async def failing_handler(event: Event):
        raise ValueError("Simulated subscriber crash!")

    async def healthy_handler(event: Event):
        succ_calls.append(event)

    # Subscribe both failing and healthy subscribers
    bus.subscribe("system.alert", failing_handler)
    bus.subscribe("system.alert", healthy_handler)

    # Publish event — failing handler should be caught safely without stopping healthy handler
    await bus.publish("system.alert", {"alert": "high"})
    await asyncio.sleep(0.05)

    assert len(succ_calls) == 1
    assert succ_calls[0].payload["alert"] == "high"
