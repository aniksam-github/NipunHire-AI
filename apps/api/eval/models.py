"""Data contracts and Pydantic models for the AI Evaluation Pipeline."""

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class FeatureType(str, Enum):
    RESUME_PARSING = "resume_parsing"
    RESUME_MATCHING = "resume_matching"
    RESUME_SCREENING = "resume_screening"


class CheckDetail(BaseModel):
    name: str
    passed: bool
    expected: Any = None
    actual: Any = None
    message: str


class AIJudgeRubric(BaseModel):
    aspects: list[str] = Field(default_factory=lambda: ["reasoning_coherence", "specificity"])
    min_score: int = 4  # Scale 1-5


class ScoreRange(BaseModel):
    min: int = 0
    max: int = 100
    field: str = "score"  # Specifies which numeric field to inspect if multi-field


class FieldMatchRule(BaseModel):
    field_path: str  # Dot notation path, e.g. "contact.email" or "factors"
    operator: str  # "is_not_none", "is_not_empty", "equals", "contains", "gte", "lte"
    value: Any = None


class ExpectedCriteria(BaseModel):
    score_range: ScoreRange | None = None
    non_empty_fields: list[str] = Field(default_factory=list)
    required_keywords: list[str] = Field(default_factory=list)
    field_rules: list[FieldMatchRule] = Field(default_factory=list)
    ai_judge_rubric: AIJudgeRubric | None = None


class TestCaseInput(BaseModel):
    resume_text: str
    job_details: dict[str, Any] | None = None


class GoldenTestCase(BaseModel):
    id: str
    feature: FeatureType
    description: str
    input: TestCaseInput
    expected_criteria: ExpectedCriteria


class TestCaseResult(BaseModel):
    case_id: str
    feature: FeatureType
    description: str
    passed: bool
    deterministic_checks: list[CheckDetail] = Field(default_factory=list)
    ai_judge_check: CheckDetail | None = None
    execution_time_seconds: float = 0.0
    error: str | None = None


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


class EvaluationRun(BaseModel):
    run_id: str
    timestamp: str
    model_version: str
    prompt_versions: dict[str, str] = Field(default_factory=dict)
    total_cases: int = 0
    passed_cases: int = 0
    failed_cases: int = 0
    aggregate_pass_rate: float = 0.0
    duration_seconds: float = 0.0
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    results: list[TestCaseResult] = Field(default_factory=list)


class AIJudgeResponse(BaseModel):
    coherence_score: int = Field(ge=1, le=5)
    specificity_score: int = Field(ge=1, le=5)
    reasoning: str
    passed: bool
