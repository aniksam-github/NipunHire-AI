"""Utilities for recovering JSON payloads from model output."""

import json


class JSONExtractionError(ValueError):
    """Raised when a response contains no valid JSON value."""


def extract_json(raw_response: str) -> str:
    """Return a canonical JSON value found anywhere in a model response.

    A direct JSON response is accepted first. Otherwise, JSON objects and
    arrays are scanned from surrounding prose or Markdown code fences.
    """
    try:
        return json.dumps(json.loads(raw_response))
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    for index, character in enumerate(raw_response):
        if character not in "[{":
            continue
        try:
            value, _ = decoder.raw_decode(raw_response[index:])
        except json.JSONDecodeError:
            continue
        return json.dumps(value)

    raise JSONExtractionError("No valid JSON found in AI response")
