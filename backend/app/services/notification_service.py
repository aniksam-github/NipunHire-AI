from beanie import PydanticObjectId
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse

def _response(item: Notification) -> NotificationResponse:
    return NotificationResponse(id=str(item.id), title=item.title, message=item.message, type=item.type, is_read=item.is_read, created_at=item.created_at)

async def create(user_id: str, title: str, message: str, type: str = "system") -> None:
    await Notification(user_id=PydanticObjectId(user_id), title=title, message=message, type=type).insert()

async def list_for_user(user_id: str) -> list[NotificationResponse]:
    rows = await Notification.find(Notification.user_id == PydanticObjectId(user_id)).sort("-created_at").to_list()
    return [_response(row) for row in rows]

async def unread_count(user_id: str) -> int:
    return await Notification.find(Notification.user_id == PydanticObjectId(user_id), Notification.is_read == False).count()  # noqa: E712

async def mark_read(user_id: str, notification_id: str) -> None:
    item = await Notification.find_one(Notification.id == PydanticObjectId(notification_id), Notification.user_id == PydanticObjectId(user_id))
    if item:
        item.is_read = True
        await item.save()

async def mark_all_read(user_id: str) -> None:
    rows = await Notification.find(Notification.user_id == PydanticObjectId(user_id), Notification.is_read == False).to_list()  # noqa: E712
    for item in rows:
        item.is_read = True
        await item.save()
