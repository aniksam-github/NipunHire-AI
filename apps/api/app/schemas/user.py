"""
Pydantic schemas for the Auth module — what crosses the HTTP boundary.

These are *transfer objects*, not database models.  They control:
  - what the client sends (UserCreate, UserLogin)
  - what the client receives (UserResponse, TokenResponse)
  - OpenAPI documentation (Field descriptions, examples)

The key rule: `hashed_password` never appears in any response schema.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    """Registration payload."""

    email: EmailStr = Field(
        ...,
        description="User's email address. Must be unique across the system.",
        examples=["recruiter@nipunhire.ai"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Plaintext password. Minimum 8 characters.",
        examples=["StrongP@ss123"],
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User's display name.",
        examples=["Jane Doe"],
    )
    role: UserRole = Field(
        default=UserRole.CANDIDATE,
        description="Account type. Defaults to 'candidate'.",
    )


class UserLogin(BaseModel):
    """Login payload."""

    email: EmailStr = Field(..., examples=["recruiter@nipunhire.ai"])
    password: str = Field(..., examples=["StrongP@ss123"])


class TokenRefreshRequest(BaseModel):
    """Payload to exchange a refresh token for a new token pair."""

    refresh_token: str = Field(
        ...,
        description="A valid, unexpired refresh token.",
    )


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class UserResponse(BaseModel):
    """
    Safe user representation — returned by all user-facing endpoints.

    `id` is a string because MongoDB ObjectIds serialize as hex strings,
    and keeping it as `str` avoids coupling the API contract to Beanie's
    PydanticObjectId type.
    """

    id: str = Field(..., description="MongoDB ObjectId as hex string.")
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token pair returned on login, registration, and refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    """
    Combined response for register/login — returns user profile + tokens
    in a single round-trip so the client doesn't need a follow-up call.
    """

    user: UserResponse
    tokens: TokenResponse
