"""
FastAPI dependency injection — the bridge between HTTP and domain logic.

This module is the *only* place where FastAPI's Depends() meets
our domain layer.  It provides:

  - get_current_user: extracts + validates the JWT from the
    Authorization header, resolves the User from the DB, and
    injects it into any route that needs an authenticated user.

  - require_role: a dependency *factory* that returns a sub-dependency
    checking the user's role.  Usage:
        @router.get("/admin", dependencies=[Depends(require_role("admin"))])

Why not put this in the router?
  - Every protected route would repeat the same decode → fetch → check
    boilerplate. A shared dependency keeps it DRY and guarantees
    consistent error handling.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.security import decode_token
from app.models.user import User
from app.repositories import user_repo

# tokenUrl points to the login endpoint for OpenAPI's "Authorize" button.
# It doesn't affect runtime behavior — it just makes /docs interactive.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Resolves the current authenticated user from the Bearer token.

    Raises HTTP 401 on any failure:
      - malformed / expired JWT
      - missing 'sub' claim
      - user no longer exists
      - account deactivated

    This is intentionally in the API-integration layer (not in
    the service) because it creates HTTPException — a FastAPI
    concept the service should never know about.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
    except JWTError:
        raise credentials_exception

    # Reject refresh tokens used as access tokens
    if payload.get("type") != "access":
        raise credentials_exception

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    return user


def require_role(*allowed_roles: str):
    """
    Dependency factory for role-based access control.

    Returns a FastAPI dependency that checks whether the current
    user's role is in the allow-list.  Raises 403 if not.

    Usage:
        @router.get(
            "/recruiter-only",
            dependencies=[Depends(require_role("recruiter", "admin"))],
        )
    """

    async def _role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role.value}' is not authorized for this action",
            )
        return current_user

    return _role_checker
