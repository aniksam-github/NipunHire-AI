"""Unit tests for global exception handlers mapping domain exceptions to HTTP responses."""

import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from fastapi import status

from app.core.ai_exceptions import AIServiceError
from app.core.exception_handlers import nipunhire_exception_handler
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DuplicateEntityError,
    EntityNotFoundError,
    NipunHireException,
)


class TestExceptionHandlers(unittest.TestCase):

    def _call_handler(self, exc: Exception):
        request = SimpleNamespace(url=SimpleNamespace(path="/api/v1/test"))
        return asyncio.run(nipunhire_exception_handler(request, exc))

    def test_entity_not_found_returns_404(self):
        res = self._call_handler(EntityNotFoundError(entity="Job", identifier="job_123"))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_duplicate_entity_returns_409(self):
        res = self._call_handler(DuplicateEntityError(entity="User", field="email"))
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)

    def test_auth_errors_return_401_and_403(self):
        res_401 = self._call_handler(AuthenticationError("Invalid token"))
        self.assertEqual(res_401.status_code, status.HTTP_401_UNAUTHORIZED)

        res_403 = self._call_handler(AuthorizationError("Forbidden"))
        self.assertEqual(res_403.status_code, status.HTTP_403_FORBIDDEN)

    def test_ai_service_error_returns_502(self):
        res = self._call_handler(AIServiceError("Model timeout"))
        self.assertEqual(res.status_code, status.HTTP_502_BAD_GATEWAY)

    def test_generic_nipunhire_exception_returns_400(self):
        res = self._call_handler(NipunHireException("Bad input"))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


if __name__ == "__main__":
    unittest.main()
