"""Deterministic safety and basic groundedness checks for AI suggestions.

These checks intentionally use narrow, explainable rules. They complement the
Phase 3A response-contract validator; they are not a general-purpose clinical
safety system or a substitute for later model-based evaluation.
"""

import re
from decimal import Decimal, InvalidOperation


class AIContentSafetyError(ValueError):
    """Raised when an AI response matches a prohibited safety pattern."""


class AIGroundednessError(ValueError):
    """Raised when a concrete summary fact is absent from the journal input."""


_PROHIBITED_PATTERNS = (
    (
        "direct mental-health diagnosis",
        re.compile(
            r"\byou (?:definitely |clearly )?(?:have|suffer from) "
            r"(?:clinical )?(?:depression|an anxiety disorder|bipolar disorder|ptsd)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "direct mental-health diagnosis",
        re.compile(
            r"\byou are (?:definitely |clearly )?"
            r"(?:clinically depressed|bipolar)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "unsafe medication instruction",
        re.compile(
            r"\b(?:stop|skip|double|increase|decrease) (?:taking )?(?:your )?"
            r"(?:prescribed )?(?:medication|medicine|dose|dosage)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "discouraging professional support",
        re.compile(
            r"\bignore (?:your )?(?:doctor|therapist|healthcare provider)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "discouraging professional support",
        re.compile(
            r"\byou (?:do not|don't) need (?:a |any )?"
            r"(?:doctor|therapist|professional help)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "encouraging self-harm",
        re.compile(
            r"\b(?:self-harm|harming yourself) (?:will|can) "
            r"(?:help|make you feel better|relieve stress)\b",
            re.IGNORECASE,
        ),
    ),
)

_ISO_DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_NUMBER_PATTERN = re.compile(r"(?<![\w-])\d+(?:\.\d+)?(?![\w-])")


def validate_ai_content_safety(ai_response):
    """Reject a small set of high-confidence unsafe instructions or claims."""
    text = "\n".join(
        [ai_response["summary"], *ai_response["self_care_tips"]]
    )

    for category, pattern in _PROHIBITED_PATTERNS:
        if pattern.search(text):
            raise AIContentSafetyError(
                f"AI response contains prohibited content: {category}."
            )

    return ai_response


def validate_basic_groundedness(ai_response, journal_entries):
    """Check concrete dates/numbers in the summary against journal evidence.

    The deterministic MVP deliberately checks only objective dates and numbers
    in the summary. Semantic relevance and subjective emotional conclusions
    require later evaluation and are outside this rule-based phase.
    """
    summary = ai_response["summary"]
    source_text = "\n".join(
        str(entry.get("notes", "")) for entry in journal_entries
    )

    summary_dates = set(_ISO_DATE_PATTERN.findall(summary))
    source_dates = {
        str(entry["entry_date"])
        for entry in journal_entries
        if entry.get("entry_date") is not None
    }
    unsupported_dates = summary_dates - source_dates
    if unsupported_dates:
        raise AIGroundednessError(
            "AI summary contains unsupported date(s): "
            + ", ".join(sorted(unsupported_dates))
        )

    summary_numbers = _extract_numbers(_ISO_DATE_PATTERN.sub("", summary))
    source_numbers = _extract_numbers(_ISO_DATE_PATTERN.sub("", source_text))
    source_numbers.add(_normalize_number(len(journal_entries)))
    source_numbers.update(
        _normalize_number(entry["mood_score"])
        for entry in journal_entries
        if entry.get("mood_score") is not None
    )

    unsupported_numbers = summary_numbers - source_numbers
    if unsupported_numbers:
        raise AIGroundednessError(
            "AI summary contains unsupported number(s): "
            + ", ".join(sorted(unsupported_numbers))
        )

    return ai_response


def _extract_numbers(text):
    return {_normalize_number(value) for value in _NUMBER_PATTERN.findall(text)}


def _normalize_number(value):
    try:
        number = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(f"Unable to normalize numeric value: {value}") from error

    normalized = format(number.normalize(), "f")
    return "0" if normalized == "-0" else normalized
