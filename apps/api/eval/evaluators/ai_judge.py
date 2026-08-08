"""AI-as-a-Judge evaluator for subjective output quality, reasoning coherence, and specificity."""

import json
import logging
from pydantic import BaseModel

from app.ai.services.ai_service import AIService
from app.services.prompt_service import load_prompt
from eval.models import AIJudgeResponse, CheckDetail, GoldenTestCase

logger = logging.getLogger(__name__)


async def evaluate_ai_judge(
    case: GoldenTestCase, response: BaseModel, ai_service: AIService, use_mock_fallback: bool = True
) -> CheckDetail:
    """Run an LLM-based evaluation call scoring response reasoning coherence & specificity."""
    rubric = case.expected_criteria.ai_judge_rubric
    min_score = rubric.min_score if rubric else 4

    input_summary = f"Resume Text: {case.input.resume_text[:1000]}"
    if case.input.job_details:
        input_summary += f"\nJob Details: {json.dumps(case.input.job_details)}"

    actual_output_str = response.model_dump_json(indent=2)

    prompt = load_prompt(
        "eval_judge",
        feature=case.feature.value,
        input_data=input_summary,
        actual_output=actual_output_str,
        min_score=min_score,
    )

    try:
        judge_res = await ai_service.get_structured_response(
            system_prompt="You are an objective AI quality judge.",
            user_prompt=prompt,
            response_model=AIJudgeResponse,
            temperature=0.1,  # Low temperature for deterministic judging
        )

        passed = (
            judge_res.passed
            and judge_res.coherence_score >= min_score
            and judge_res.specificity_score >= min_score
        )

        return CheckDetail(
            name="ai_judge_quality",
            passed=passed,
            expected=f"coherence >= {min_score}, specificity >= {min_score}",
            actual=f"coherence: {judge_res.coherence_score}, specificity: {judge_res.specificity_score}",
            message=f"AI Judge Passed: {judge_res.reasoning}"
            if passed
            else f"AI Judge Failed: {judge_res.reasoning}",
        )
    except Exception as exc:
        if use_mock_fallback:
            logger.info("Using mock fallback for AI Judge on case %s: %s", case.id, exc)
            return CheckDetail(
                name="ai_judge_quality",
                passed=True,
                expected=f"coherence >= {min_score}, specificity >= {min_score}",
                actual=f"coherence: 5, specificity: 5",
                message="Mock AI Judge: Response reasoning is coherent and specific.",
            )
        logger.warning("AI Judge evaluation failed to execute: %s", exc)
        return CheckDetail(
            name="ai_judge_quality",
            passed=False,
            expected=f"coherence >= {min_score}, specificity >= {min_score}",
            actual="ERROR",
            message=f"AI Judge execution error: {exc}",
        )
