"""
Authentication service — all auth business logic lives here.

This module orchestrates:
  - Registration (duplicate check → hash → persist)
  - Login (fetch → verify → token issue)
  - Token refresh (decode → validate type → re-issue)

It calls the repository for data access and core/security for
cryptographic operations.  It raises domain exceptions (never
HTTP exceptions) so it stays framework-agnostic.
"""

import logging

from jose import JWTError

from app.core.exceptions import (
    AuthenticationError,
    DuplicateEntityError,
    EntityNotFoundError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories import user_repo
from app.schemas.user import (
    AuthResponse,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

logger = logging.getLogger(__name__)


def _build_user_response(user: User) -> UserResponse:
    """
    Maps a Beanie User document to a UserResponse schema.

    Centralised here so every code path returns the same shape —
    avoids the risk of one endpoint leaking `hashed_password`
    because someone forgot to exclude it.
    """
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


def _build_tokens(user: User) -> TokenResponse:
    """Issues an access + refresh token pair for a given user."""
    return TokenResponse(
        access_token=create_access_token(subject=str(user.id)),
        refresh_token=create_refresh_token(subject=str(user.id)),
    )


async def register_user(data: UserCreate) -> AuthResponse:
    """
    Registers a new user account.

    Flow:
      1. Check if email is already taken → DuplicateEntityError
      2. Hash the plaintext password
      3. Persist the User document
      4. Issue tokens immediately (no separate login step needed)

    Returns an AuthResponse (user profile + tokens) so the client
    is authenticated in a single round-trip.
    """
    existing = await user_repo.get_by_email(data.email)
    if existing is not None:
        raise DuplicateEntityError(entity="User", field="email")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
    )

    user = await user_repo.create(user)
    logger.info("User registered: %s (role=%s)", user.email, user.role.value)

    return AuthResponse(
        user=_build_user_response(user),
        tokens=_build_tokens(user),
    )


async def authenticate_user(data: UserLogin) -> AuthResponse:
    """
    Authenticates an existing user via email + password.

    Flow:
      1. Fetch user by email → AuthenticationError if not found
      2. Verify password → AuthenticationError if mismatch
      3. Check account is active → AuthenticationError if suspended
      4. Issue tokens

    We use the same generic "Invalid email or password" message for
    both "user not found" and "wrong password" to avoid user enumeration.
    """
    user = await user_repo.get_by_email(data.email)
    if user is None:
        raise AuthenticationError(detail="Invalid email or password")

    if not verify_password(data.password, user.hashed_password):
        raise AuthenticationError(detail="Invalid email or password")

    if not user.is_active:
        raise AuthenticationError(detail="Account is deactivated")

    logger.info("User authenticated: %s", user.email)

    return AuthResponse(
        user=_build_user_response(user),
        tokens=_build_tokens(user),
    )


async def refresh_access_token(refresh_token: str) -> TokenResponse:
    """
    Exchanges a valid refresh token for a new access + refresh pair.

    Why issue a *new* refresh token too (token rotation)?
      - If a refresh token is stolen, the attacker and legitimate user
        will race to use it.  The first use invalidates the old one
        (conceptually — we rely on short-lived JWTs here, but the
        pattern is in place for future DB-backed revocation).
    """
    try:
        payload = decode_token(refresh_token)
    except JWTError as exc:
        raise AuthenticationError(detail="Invalid or expired refresh token") from exc

    if payload.get("type") != "refresh":
        raise AuthenticationError(detail="Token is not a refresh token")

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise AuthenticationError(detail="Token payload missing subject")

    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise EntityNotFoundError(entity="User", identifier=user_id)

    if not user.is_active:
        raise AuthenticationError(detail="Account is deactivated")

    logger.info("Tokens refreshed for user: %s", user.email)

    return _build_tokens(user)


async def get_current_user_profile(user: User) -> UserResponse:
    """
    Returns the profile of an already-authenticated user.

    The User instance is resolved by the dependency layer
    (core/dependencies.py) before this function is called,
    so there's no token parsing here — just mapping.
    """
    return _build_user_response(user)


async def change_password(user: User, current_password: str, new_password: str) -> None:
    if not verify_password(current_password, user.hashed_password):
        raise AuthenticationError(detail="Current password is incorrect")
    user.hashed_password = hash_password(new_password)
    await user.save()
