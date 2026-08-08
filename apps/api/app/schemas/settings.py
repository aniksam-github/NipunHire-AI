from pydantic import BaseModel, Field


class AccountSettingsUpdate(BaseModel):
    theme: str | None = Field(default=None, pattern="^(light|dark|system)$")
    notifications_enabled: bool | None = None
    email_notifications_enabled: bool | None = None
    selected_ai_model: str | None = Field(default=None, max_length=80)


class AccountSettingsResponse(BaseModel):
    theme: str
    notifications_enabled: bool
    email_notifications_enabled: bool
    selected_ai_model: str


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)
