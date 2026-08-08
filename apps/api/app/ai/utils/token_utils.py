"""Dependency-free token-count estimation for prompt budgeting."""

import math
import re


def estimate_token_count(text: str, model: str = "gpt-4o-mini") -> int:
    """Estimate tokens for an OpenAI model without network or SDK calls.

    Pass the configured ``OPENAI_MODEL`` at call sites when it differs from
    the default. This deterministic approximation budgets four characters
    per token and counts punctuation separately; it is not billing-accurate.
    """
    del model  # Kept in the API so callers can pass their configured model.
    if not text:
        return 0

    units = re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)
    return sum(max(1, math.ceil(len(unit) / 4)) for unit in units)
