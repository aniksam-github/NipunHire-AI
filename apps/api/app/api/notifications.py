from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationCount, NotificationResponse
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=list[NotificationResponse])
async def list_notifications(current_user: User = Depends(get_current_user)):
    return await notification_service.list_for_user(str(current_user.id))

@router.get("/unread-count", response_model=NotificationCount)
async def get_unread_count(current_user: User = Depends(get_current_user)):
    return NotificationCount(unread_count=await notification_service.unread_count(str(current_user.id)))

@router.patch("/{notification_id}/read", status_code=204)
async def mark_read(notification_id: str, current_user: User = Depends(get_current_user)):
    await notification_service.mark_read(str(current_user.id), notification_id)

@router.post("/read-all", status_code=204)
async def mark_all_read(current_user: User = Depends(get_current_user)):
    await notification_service.mark_all_read(str(current_user.id))
