"""Deterministic checks evaluator for AI feature outputs."""

from typing import Any
from pydantic import BaseModel

from eval.models import CheckDetail, GoldenTestCase


def _get_field_value(obj: Any, field_path: str) -> tuple[bool, Any]:
    """Retrieve field value using dot-notation (e.g. 'contact.email')."""
    current = obj
    for part in field_path.split("."):
        if isinstance(current, BaseModel):
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                return False, None
        elif isinstance(current, dict):
            if part in current:
                current = current[part]
            else:
                return False, None
        else:
            return False, None
    return True, current


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, (str, list, dict, set, tuple)):
        return len(value) == 0
    return False


def evaluate_deterministic(case: GoldenTestCase, response: BaseModel) -> list[CheckDetail]:
    """Run all deterministic checks defined in expected_criteria against the AI response."""
    checks: list[CheckDetail] = []
    criteria = case.expected_criteria

    # 1. Score Range Check
    if criteria.score_range:
        field_name = criteria.score_range.field or "score"
        found, val = _get_field_value(response, field_name)
        if not found or val is None:
            # Fallback search for common score attributes if specified field not found
            for fallback in ["overall_match_percentage", "ats_compatibility_score", "score"]:
                found, val = _get_field_value(response, fallback)
                if found and val is not None:
                    break

        if found and isinstance(val, (int, float)):
            in_range = criteria.score_range.min <= val <= criteria.score_range.max
            checks.append(
                CheckDetail(
                    name=f"score_range ({field_name})",
                    passed=in_range,
                    expected=f"[{criteria.score_range.min}, {criteria.score_range.max}]",
                    actual=val,
                    message=f"Score {val} within range [{criteria.score_range.min}, {criteria.score_range.max}]"
                    if in_range
                    else f"Score {val} outside expected range [{criteria.score_range.min}, {criteria.score_range.max}]",
                )
            )
        else:
            checks.append(
                CheckDetail(
                    name=f"score_range ({field_name})",
                    passed=False,
                    expected=f"[{criteria.score_range.min}, {criteria.score_range.max}]",
                    actual=val,
                    message=f"Numeric score field '{field_name}' was not found in response",
                )
            )

    # 2. Non-empty Fields Check
    for field_path in criteria.non_empty_fields:
        found, val = _get_field_value(response, field_path)
        passed = found and not _is_empty(val)
        checks.append(
            CheckDetail(
                name=f"non_empty_field ({field_path})",
                passed=passed,
                expected="non-empty value",
                actual="[empty]" if _is_empty(val) else str(val)[:50],
                message=f"Field '{field_path}' is present and non-empty"
                if passed
                else f"Field '{field_path}' is empty or missing",
            )
        )

    # 3. Required Keywords Check
    if criteria.required_keywords:
        serialized_text = (
            response.model_dump_json().lower()
            if isinstance(response, BaseModel)
            else str(response).lower()
        )
        for kw in criteria.required_keywords:
            kw_lower = kw.lower()
            found = kw_lower in serialized_text
            checks.append(
                CheckDetail(
                    name=f"required_keyword ({kw})",
                    passed=found,
                    expected=kw,
                    actual="present" if found else "absent",
                    message=f"Keyword '{kw}' found in response output"
                    if found
                    else f"Keyword '{kw}' missing from response output",
                )
            )

    # 4. Custom Field Rules
    for rule in criteria.field_rules:
        found, val = _get_field_value(response, rule.field_path)
        op = rule.operator.lower()
        passed = False
        actual_desc = str(val)

        if op == "is_none":
            passed = val is None
        elif op == "is_not_none":
            passed = val is not None
        elif op == "is_not_empty":
            passed = found and not _is_empty(val)
        elif op == "equals":
            passed = found and val == rule.value
        elif op == "contains":
            if isinstance(val, (list, str)):
                passed = str(rule.value).lower() in str(val).lower()
            else:
                passed = False
        elif op == "gte":
            passed = found and isinstance(val, (int, float)) and val >= rule.value
        elif op == "lte":
            passed = found and isinstance(val, (int, float)) and val <= rule.value

        checks.append(
            CheckDetail(
                name=f"field_rule ({rule.field_path} {op} {rule.value})",
                passed=passed,
                expected=f"{op} {rule.value}",
                actual=actual_desc[:50],
                message=f"Rule '{rule.field_path} {op} {rule.value}' satisfied"
                if passed
                else f"Rule '{rule.field_path} {op} {rule.value}' failed (got {actual_desc[:50]})",
            )
        )

    return checks
