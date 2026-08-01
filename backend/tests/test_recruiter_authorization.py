"""Authorization tests for Phase 8 Recruiter AI endpoints and dependencies."""

import asyncio
import unittest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException, status

from app.core.dependencies import require_role
from app.models.user import User, UserRole


class TestRecruiterAuthorization(unittest.TestCase):

    def test_candidate_role_denied_access_with_403_forbidden(self):
        candidate_user = User.model_construct(
            id="cand_123",
            email="candidate@nipunhire.ai",
            full_name="Candidate User",
            role=UserRole.CANDIDATE,
            is_active=True,
        )

        role_dependency = require_role("recruiter", "admin")

        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(role_dependency(current_user=candidate_user))

        self.assertEqual(ctx.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("not authorized", ctx.exception.detail)

    def test_recruiter_role_granted_access(self):
        recruiter_user = User.model_construct(
            id="rec_123",
            email="recruiter@nipunhire.ai",
            full_name="Recruiter User",
            role=UserRole.RECRUITER,
            is_active=True,
        )

        role_dependency = require_role("recruiter", "admin")
        user = asyncio.run(role_dependency(current_user=recruiter_user))
        self.assertEqual(user.role, UserRole.RECRUITER)

    def test_admin_role_granted_access(self):
        admin_user = User.model_construct(
            id="admin_123",
            email="admin@nipunhire.ai",
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True,
        )

        role_dependency = require_role("recruiter", "admin")
        user = asyncio.run(role_dependency(current_user=admin_user))
        self.assertEqual(user.role, UserRole.ADMIN)


if __name__ == "__main__":
    unittest.main()
