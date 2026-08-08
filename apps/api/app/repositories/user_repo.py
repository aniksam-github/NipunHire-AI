"""
User repository — data-access layer for the `users` collection.

Every database query for users goes through this module.  The service
layer calls these functions; it never imports Beanie directly.

Why a thin wrapper around Beanie?
  1. If we later swap Beanie for raw Motor aggregations (e.g., for
     vector-search pipelines), only this file changes.
  2. Unit-testing services becomes trivial: mock the repo, skip the DB.
  3. Query logic stays in one place — no Beanie calls scattered across
     routers, services, and utilities.
"""

from beanie import PydanticObjectId

from app.models.user import User


async def get_by_email(email: str) -> User | None:
    """Fetch a single user by email. Returns None if not found."""
    try:
        return await User.find_one({"email": email})
    except Exception:
        return None


async def get_by_id(user_id: str) -> User | None:
    """
    Fetch a single user by their MongoDB ObjectId.

    Accepts a plain string and converts internally so callers
    (services, dependencies) don't need to know about PydanticObjectId.
    """
    try:
        return await User.get(PydanticObjectId(user_id))
    except Exception:
        return None


async def create(user: User) -> User:
    """
    Persist a new User document.

    The caller (auth_service) is responsible for setting
    `hashed_password` before calling this — the repo does not
    know anything about password hashing.
    """
    await user.insert()
    return user
