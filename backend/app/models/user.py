"""
User document — Beanie ODM model mapped to the `users` MongoDB collection.

This is a *data model*, not a domain entity.  It defines:
  - what fields exist in the DB
  - indexes for query performance
  - collection-level settings

Business rules (password hashing, duplicate checks) live in the
service layer; this file stays a dumb data container.
"""

from datetime import datetime, timezone
from enum import Enum

from beanie import Document, Indexed
from pydantic import EmailStr, Field


class UserRole(str, Enum):
    """
    Enum for user roles.

    Using str + Enum so roles serialize as plain strings in JSON/MongoDB
    while still getting type-safety and autocompletion in Python.
    """

    RECRUITER = "recruiter"
    CANDIDATE = "candidate"
    ADMIN = "admin"


class User(Document):
    """
    Represents a registered user in the system.

    Indexes:
      - email (unique): fast lookups during login, duplicate prevention.
      - role: will be used for filtered queries (e.g., "all recruiters").
    """

    email: Indexed(EmailStr, unique=True)  # type: ignore[valid-type]
    hashed_password: str
    full_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = Field(default=UserRole.CANDIDATE)
    is_active: bool = Field(default=True)
    theme: str = Field(default="system")
    notifications_enabled: bool = Field(default=True)
    email_notifications_enabled: bool = Field(default=True)
    selected_ai_model: str = Field(default="default")

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"

    class Config:
        json_schema_extra = {
            "example": {
                "email": "recruiter@hiresense.ai",
                "hashed_password": "$2b$12$...",
                "full_name": "Jane Doe",
                "role": "recruiter",
                "is_active": True,
            }
        }
