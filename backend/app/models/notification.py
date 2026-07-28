from datetime import datetime, timezone
from beanie import Document, PydanticObjectId
from pydantic import Field


class Notification(Document):
    user_id: PydanticObjectId
    title: str = Field(max_length=160)
    message: str = Field(max_length=500)
    type: str = Field(default="system", max_length=40)
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "notifications"
        indexes = ["user_id", "is_read", [("created_at", -1)]]
