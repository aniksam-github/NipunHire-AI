import asyncio
import unittest

from pydantic import ValidationError

from app.schemas.resume_intelligence import ResumeParsingResult
from app.schemas.resume_screening import (
    CategorizedSkillsResult,
    ResumeAnalysisResult,
    ResumeImprovementResult,
)
from app.services.resume_screening_service import (
    analyze_profile,
    extract_categorized_skills,
    generate_improvements,
)


class FakeAIService:
    def __init__(self):
        self.calls = []

    async def get_structured_response(self, **kwargs):
        self.calls.append(kwargs)
        response_model = kwargs["response_model"]
        if response_model is ResumeAnalysisResult:
            return ResumeAnalysisResult(
                strengths=["Python"],
                weaknesses=["No cloud experience"],
                ats_compatibility_score=82,
                improvement_suggestions=["Add deployment work"],
                confidence_score=91,
            )
        if response_model is CategorizedSkillsResult:
            return CategorizedSkillsResult(technical_skills=["Python"], tools=["Git"])
        return ResumeImprovementResult(
            recommended_projects=["Deploy an API"],
            skills_to_learn=["AWS"],
            certifications=[],
            missing_keywords=["Docker"],
        )


class ResumeScreeningSchemaTests(unittest.TestCase):
    def test_analysis_schema_enforces_score_bounds(self):
        valid = ResumeAnalysisResult(
            strengths=[], weaknesses=[], ats_compatibility_score=0,
            improvement_suggestions=[], confidence_score=100,
        )
        self.assertEqual(valid.confidence_score, 100)
        with self.assertRaises(ValidationError):
            ResumeAnalysisResult(ats_compatibility_score=101, confidence_score=50)

    def test_categorized_skills_schema_rejects_wrong_list_type(self):
        self.assertEqual(CategorizedSkillsResult(frameworks=["FastAPI"]).frameworks, ["FastAPI"])
        with self.assertRaises(ValidationError):
            CategorizedSkillsResult(tools="Git")

    def test_improvement_schema_rejects_wrong_list_type(self):
        self.assertEqual(ResumeImprovementResult(skills_to_learn=["AWS"]).skills_to_learn, ["AWS"])
        with self.assertRaises(ValidationError):
            ResumeImprovementResult(missing_keywords=123)


class ResumeScreeningServiceTests(unittest.TestCase):
    def test_improvement_uses_previous_stage_results(self):
        parsed = ResumeParsingResult(full_name="Jane Doe", skills=["Python"])
        service = FakeAIService()

        analysis = asyncio.run(analyze_profile(parsed, service))
        skills = asyncio.run(extract_categorized_skills(parsed, service))
        improvements = asyncio.run(generate_improvements(parsed, analysis, skills, service))

        self.assertEqual(improvements.skills_to_learn, ["AWS"])
        improvement_prompt = service.calls[2]["user_prompt"]
        self.assertIn("No cloud experience", improvement_prompt)
        self.assertIn("Git", improvement_prompt)
        self.assertEqual(len(service.calls), 3)


if __name__ == "__main__":
    unittest.main()
