from datetime import datetime
from pydantic import BaseModel

class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime

class NotificationCount(BaseModel):
    unread_count: int
