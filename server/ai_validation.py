"""Deterministic parsing and contract validation for AI suggestion responses."""

import json


MAX_SUMMARY_LENGTH = 1000
MAX_SERIALIZED_TIPS_LENGTH = 2000


class AIResponseValidationError(ValueError):
    """Raised when an AI provider response violates the application contract."""


def _strip_standard_code_fence(text):
    """Remove a complete ```json or plain ``` wrapper without guessing content."""
    lines = text.splitlines()
    if len(lines) < 3:
        return text

    opening = lines[0].strip().lower()
    closing = lines[-1].strip()
    if opening in {"```json", "```"} and closing == "```":
        return "\n".join(lines[1:-1]).strip()
    return text


def parse_and_validate_ai_response(raw_response):
    """Return a normalized response or raise AIResponseValidationError."""
    if not isinstance(raw_response, str):
        raise AIResponseValidationError("AI response must be a string.")

    cleaned_response = _strip_standard_code_fence(raw_response.strip())
    try:
        parsed = json.loads(cleaned_response)
    except json.JSONDecodeError as error:
        raise AIResponseValidationError(
            "AI response must contain valid JSON."
        ) from error

    if not isinstance(parsed, dict):
        raise AIResponseValidationError("AI response must be a JSON object.")

    if "summary" not in parsed:
        raise AIResponseValidationError("AI response must contain summary.")
    if "self_care_tips" not in parsed:
        raise AIResponseValidationError("AI response must contain self_care_tips.")

    summary = parsed["summary"]
    if not isinstance(summary, str) or not summary.strip():
        raise AIResponseValidationError("summary must be a non-empty string.")
    summary = summary.strip()
    if len(summary) > MAX_SUMMARY_LENGTH:
        raise AIResponseValidationError(
            f"summary must not exceed {MAX_SUMMARY_LENGTH} characters."
        )

    tips = parsed["self_care_tips"]
    if not isinstance(tips, list):
        raise AIResponseValidationError("self_care_tips must be a list.")
    if len(tips) != 3:
        raise AIResponseValidationError(
            "self_care_tips must contain exactly 3 items."
        )

    normalized_tips = []
    for tip in tips:
        if not isinstance(tip, str) or not tip.strip():
            raise AIResponseValidationError(
                "Each self-care tip must be a non-empty string."
            )
        normalized_tips.append(tip.strip())

    if len(json.dumps(normalized_tips)) > MAX_SERIALIZED_TIPS_LENGTH:
        raise AIResponseValidationError(
            "self_care_tips exceed the maximum serialized length."
        )

    return {
        "summary": summary,
        "self_care_tips": normalized_tips,
    }
