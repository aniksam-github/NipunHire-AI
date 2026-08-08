import unittest

from pydantic import BaseModel

from app.ai.services.ai_service import AIService
from app.core.ai_exceptions import AIResponseValidationError


class Result(BaseModel):
    answer: str


class AIServiceTests(unittest.TestCase):
    def test_validate_response_returns_typed_model(self):
        result = AIService._validate_response('{"answer": "ok"}', Result)
        self.assertEqual(result.answer, "ok")

    def test_validate_response_rejects_invalid_json(self):
        with self.assertRaises(AIResponseValidationError):
            AIService._validate_response("not-json", Result)

    def test_backoff_grows_by_attempt(self):
        self.assertGreaterEqual(AIService._compute_backoff(2), 2)


if __name__ == "__main__":
    unittest.main()
