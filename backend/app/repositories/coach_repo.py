"""Persistence operations for the existing career-coach history."""

from beanie import PydanticObjectId

from app.models.coach import CoachMessage


async def create(message: CoachMessage) -> CoachMessage:
    return await message.insert()


async def list_by_candidate(candidate_id: str) -> list[CoachMessage]:
    return await CoachMessage.find(
        CoachMessage.candidate_id == PydanticObjectId(candidate_id)
    ).sort("-created_at").to_list()
