"""Explainable contracts for candidate-profile to job matching.

Factor-level contributions make each match score auditable: recruiters can see
which named evidence increased or reduced the score instead of receiving a
black-box percentage. This supports review, contestability, and research.
"""

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class MatchFactor(BaseModel):
    """One named, evidence-based contribution to an overall match score."""

    name: str = Field(min_length=1)
    point_contribution: int = Field(ge=-100, le=100)
    reason: str = Field(min_length=1)


class BaseMatchResult(BaseModel):
    overall_match_percentage: int = Field(ge=0, le=100)
    missing_skills: list[str] = Field(default_factory=list)
    score_reasoning: str = Field(min_length=1)
    factors: list[MatchFactor] = Field(min_length=1)

    @model_validator(mode="after")
    def factor_contributions_reconcile_with_score(self):
        """Reject AI output whose factor arithmetic does not explain its score."""
        contribution_total = sum(factor.point_contribution for factor in self.factors)
        if contribution_total != self.overall_match_percentage:
            raise ValueError(
                "Factor contributions must sum to overall_match_percentage "
                f"({contribution_total} != {self.overall_match_percentage})"
            )
        return self


class RecruiterRecommendation(str, Enum):
    HIRE = "Hire"
    MAYBE = "Maybe"
    REJECT = "Reject"


class MatchRecommendation(BaseModel):
    recommendation: RecruiterRecommendation
    reason: str = Field(min_length=1)


class ExplainableMatchResponse(BaseModel):
    id: str
    profile_id: str
    job_id: str
    result: BaseMatchResult
    recommendation: MatchRecommendation
