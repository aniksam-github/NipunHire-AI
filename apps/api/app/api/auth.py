"""
Auth API router — HTTP endpoints for registration, login, token refresh,
and profile retrieval.

This is the thinnest possible layer.  Each route:
  1. Accepts a Pydantic schema (FastAPI validates the body automatically)
  2. Calls the auth service (which contains the actual logic)
  3. Returns a Pydantic response schema

Domain exceptions raised by the service are caught here and translated
into the appropriate HTTP status codes.  The service never imports
FastAPI; this file is the *only* place where domain meets HTTP.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.core.exceptions import (
    AuthenticationError,
    DuplicateEntityError,
    EntityNotFoundError,
)
from app.models.user import User
from app.schemas.user import (
    AuthResponse,
    TokenRefreshRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.schemas.settings import PasswordChangeRequest
from app.services import auth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description=(
        "Creates a new user with the given credentials and returns "
        "the user profile along with access and refresh tokens."
    ),
)
async def register(data: UserCreate) -> AuthResponse:
    try:
        return await auth_service.register_user(data)
    except DuplicateEntityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=exc.detail,
        ) from exc


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Authenticate and receive tokens",
    description=(
        "Validates email and password, returns user profile "
        "along with access and refresh tokens."
    ),
)
async def login(data: UserLogin) -> AuthResponse:
    try:
        return await auth_service.authenticate_user(data)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.detail,
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


# ---------------------------------------------------------------------------
# POST /auth/refresh
# ---------------------------------------------------------------------------


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh an expired access token",
    description=(
        "Exchanges a valid refresh token for a new access + refresh "
        "token pair. The old refresh token should be discarded."
    ),
)
async def refresh(data: TokenRefreshRequest) -> TokenResponse:
    try:
        return await auth_service.refresh_access_token(data.refresh_token)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.detail,
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except EntityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.detail,
        ) from exc


# ---------------------------------------------------------------------------
# GET /auth/me
# ---------------------------------------------------------------------------


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description=(
        "Returns the profile of the authenticated user. "
        "Requires a valid access token in the Authorization header."
    ),
)
async def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return await auth_service.get_current_user_profile(current_user)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(data: PasswordChangeRequest, current_user: User = Depends(get_current_user)):
    try:
        await auth_service.change_password(current_user, data.current_password, data.new_password)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.detail) from exc
