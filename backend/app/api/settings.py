from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.settings import AccountSettingsResponse, AccountSettingsUpdate

router = APIRouter(prefix="/settings", tags=["Settings"])


def _response(user: User) -> AccountSettingsResponse:
    return AccountSettingsResponse(theme=user.theme, notifications_enabled=user.notifications_enabled,
        email_notifications_enabled=user.email_notifications_enabled, selected_ai_model=user.selected_ai_model)


@router.get("/me", response_model=AccountSettingsResponse)
async def get_settings(current_user: User = Depends(get_current_user)):
    return _response(current_user)


@router.patch("/me", response_model=AccountSettingsResponse)
async def update_settings(data: AccountSettingsUpdate, current_user: User = Depends(get_current_user)):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    await current_user.save()
    return _response(current_user)
