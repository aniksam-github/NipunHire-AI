import asyncio
import unittest

from app.schemas.ai import ResumeAnalysis
from app.services.openai_service import OpenAIService
from app.services.prompt_service import load_prompt


class FakeResponses:
    async def parse(self, **kwargs):
        self.kwargs = kwargs
        return type("Response", (), {"output_parsed": {"summary": "Strong backend candidate", "skills": ["Python"]}})()


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


class AIFoundationTests(unittest.TestCase):
    def test_prompt_is_loaded_from_file(self):
        self.assertIn("Jane Doe", load_prompt("candidate_summary", candidate_text="Jane Doe"))

    def test_generate_returns_validated_model(self):
        client = FakeClient()
        result = asyncio.run(OpenAIService(client).generate("Analyse this", ResumeAnalysis))

        self.assertEqual(result.skills, ["Python"])
        self.assertEqual(client.responses.kwargs["text_format"], ResumeAnalysis)


if __name__ == "__main__":
    unittest.main()
