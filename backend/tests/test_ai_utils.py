import json
import unittest

from app.ai.utils.json_utils import JSONExtractionError, extract_json
from app.ai.utils.token_utils import estimate_token_count


class JSONUtilsTests(unittest.TestCase):
    def test_returns_clean_json(self):
        self.assertEqual(json.loads(extract_json('{"score": 90}')), {"score": 90})

    def test_extracts_json_from_markdown_fence(self):
        response = "Result:\n```json\n{\"skills\": [\"Python\"]}\n```"
        self.assertEqual(json.loads(extract_json(response)), {"skills": ["Python"]})

    def test_raises_when_response_has_no_json(self):
        with self.assertRaisesRegex(JSONExtractionError, "No valid JSON"):
            extract_json("No structured result was returned.")


class TokenUtilsTests(unittest.TestCase):
    def test_longer_text_has_more_estimated_tokens(self):
        self.assertEqual(estimate_token_count(""), 0)
        self.assertGreater(estimate_token_count("A longer sentence has more tokens."), estimate_token_count("Short."))


if __name__ == "__main__":
    unittest.main()
