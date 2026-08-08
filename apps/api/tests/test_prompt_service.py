import unittest

from app.services.prompt_service import PromptNotFoundError, load_prompt


class PromptServiceTests(unittest.TestCase):
    def test_loads_and_renders_named_template(self):
        prompt = load_prompt("resume_matching", profile_json="Candidate", job_json="Role")
        self.assertIn("Candidate", prompt)
        self.assertIn("Role", prompt)

    def test_missing_template_has_specific_error(self):
        with self.assertRaisesRegex(PromptNotFoundError, "does-not-exist"):
            load_prompt("does-not-exist")


if __name__ == "__main__":
    unittest.main()
