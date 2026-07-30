import asyncio
import unittest

from pydantic import ValidationError

from app.core.matching_exceptions import ResumeMatchingError
from app.schemas.resume_intelligence import ResumeParsingResult
from app.schemas.resume_matching import (
    BaseMatchResult,
    MatchFactor,
    MatchRecommendation,
    RecruiterRecommendation,
)
from app.services.resume_matching_service import analyze_match, derive_recommendation


def valid_match_result() -> BaseMatchResult:
    return BaseMatchResult(
        overall_match_percentage=70,
        missing_skills=["Docker"],
        score_reasoning="Python experience offsets a Docker gap.",
        factors=[
            MatchFactor(name="Python", point_contribution=85, reason="Profile lists Python projects."),
            MatchFactor(name="Docker", point_contribution=-15, reason="Profile does not evidence Docker."),
        ],
    )


class FakeAIService:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def get_structured_response(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


class ResumeMatchingSchemaTests(unittest.TestCase):
    def test_factor_contributions_must_sum_to_score(self):
        self.assertEqual(valid_match_result().overall_match_percentage, 70)
        with self.assertRaises(ValidationError):
            BaseMatchResult(
                overall_match_percentage=70,
                missing_skills=[],
                score_reasoning="Inconsistent arithmetic.",
                factors=[MatchFactor(name="Python", point_contribution=60, reason="Evidence exists.")],
            )

    def test_recommendation_is_enum_restricted(self):
        self.assertEqual(
            MatchRecommendation(recommendation="Hire", reason="Strong evidence.").recommendation,
            RecruiterRecommendation.HIRE,
        )
        with self.assertRaises(ValidationError):
            MatchRecommendation(recommendation="Definitely", reason="Invalid enum.")

    def test_recommendation_reason_is_required(self):
        with self.assertRaises(ValidationError):
            MatchRecommendation(recommendation="Maybe", reason="")


class ResumeMatchingServiceTests(unittest.TestCase):
    def test_mocked_ai_result_returns_explainable_match(self):
        service = FakeAIService(valid_match_result())
        profile = ResumeParsingResult(full_name="Jane", skills=["Python"])
        result = asyncio.run(analyze_match(profile, {"title": "Backend Engineer"}, service))
        recommendation = derive_recommendation(result)
        self.assertEqual(result.factors[0].name, "Python")
        self.assertEqual(recommendation.recommendation, RecruiterRecommendation.MAYBE)
        self.assertEqual(len(service.calls), 1)

    def test_service_rejects_mocked_unreconciled_result(self):
        invalid = BaseMatchResult.model_construct(
            overall_match_percentage=70,
            missing_skills=[],
            score_reasoning="Bypassed validation.",
            factors=[MatchFactor(name="Python", point_contribution=60, reason="Evidence exists.")],
        )
        with self.assertRaises(ResumeMatchingError):
            asyncio.run(
                analyze_match(
                    ResumeParsingResult(full_name="Jane"),
                    {"title": "Backend Engineer"},
                    FakeAIService(invalid),
                )
            )


if __name__ == "__main__":
    unittest.main()
