from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import jwt

from app.core.config import settings


def hash_password(plain_password: str) -> str:
    """
    Hashes a plaintext password for storage using bcrypt directly.

    We use bcrypt directly instead of passlib because passlib is
    unmaintained and broken with bcrypt>=4.1. Direct bcrypt is
    simpler, has zero compatibility issues, and the API is stable.
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a stored bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def _create_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    """
    Internal helper — encodes a JWT with standard claims.

    Not exported directly; access/refresh functions below are the
    public API so callers can never forget to set `type`.
    """
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )


def create_access_token(subject: str) -> str:
    """
    Issues a short-lived access token.

    `subject` is the user's id (string) — kept generic (not `user_id`)
    since JWT convention names this claim `sub`.
    """
    return _create_token(
        subject=subject,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )


def create_refresh_token(subject: str) -> str:
    """Issues a long-lived refresh token, used only to mint new access tokens."""
    return _create_token(
        subject=subject,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    Decodes and verifies a JWT's signature and expiry.

    Raises jose.JWTError (or subclasses like ExpiredSignatureError) on
    failure — callers (API-layer dependencies) are responsible for
    catching this and translating it into an HTTP 401. This function
    stays framework-agnostic on purpose.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET.get_secret_value(),
        algorithms=[settings.JWT_ALGORITHM],
    )