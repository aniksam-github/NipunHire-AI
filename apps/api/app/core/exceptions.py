"""
Domain-specific exceptions for NipunHire AI.

These are business-logic exceptions — they carry semantic meaning
("duplicate email", "invalid credentials") but know nothing about HTTP.

The API layer catches these and translates them into the appropriate
HTTP status codes (409, 401, 404, etc.).  This separation means the
service layer stays framework-agnostic and testable without FastAPI.
"""


class NipunHireException(Exception):
    """
    Base exception for all NipunHire domain errors.

    Every custom exception inherits from this, so a single
    `except NipunHireException` in the API layer catches all
    domain-level failures without accidentally swallowing
    unrelated system errors (KeyError, ValueError, etc.).
    """

    def __init__(self, detail: str = "An unexpected error occurred"):
        self.detail = detail
        super().__init__(self.detail)


class DuplicateEntityError(NipunHireException):
    """Raised when attempting to create an entity that already exists (e.g., duplicate email)."""

    def __init__(self, entity: str = "Entity", field: str = "identifier"):
        super().__init__(detail=f"{entity} with this {field} already exists")


class AuthenticationError(NipunHireException):
    """Raised when authentication fails (wrong password, expired token, etc.)."""

    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(detail=detail)


class EntityNotFoundError(NipunHireException):
    """Raised when a requested entity does not exist in the database."""

    def __init__(self, entity: str = "Entity", identifier: str = ""):
        detail = f"{entity} not found"
        if identifier:
            detail = f"{entity} with id '{identifier}' not found"
        super().__init__(detail=detail)


class AuthorizationError(NipunHireException):
    """Raised when a user lacks permission for the requested action."""

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(detail=detail)
