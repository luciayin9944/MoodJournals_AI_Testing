import json
from pathlib import Path

import pytest

from ai_safety import (
    AIContentSafetyError,
    AIGroundednessError,
    validate_ai_content_safety,
    validate_basic_groundedness,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "provider_responses.json"


@pytest.fixture(scope="module")
def provider_responses():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_safe_supportive_response_is_accepted(provider_responses):
    response = provider_responses["safe_supportive_response"]

    assert validate_ai_content_safety(response) == response


def test_recommending_professional_support_is_accepted(provider_responses):
    response = provider_responses["safe_professional_support"]

    assert validate_ai_content_safety(response) == response


@pytest.mark.parametrize(
    "fixture_name",
    [
        "unsafe_diagnosis",
        "unsafe_medication_advice",
        "unsafe_ignore_professional",
        "unsafe_harm_encouragement",
    ],
)
def test_prohibited_safety_content_is_rejected(provider_responses, fixture_name):
    with pytest.raises(AIContentSafetyError):
        validate_ai_content_safety(provider_responses[fixture_name])


def test_supported_dates_and_numbers_are_accepted(provider_responses):
    entries = [
        {"entry_date": "2026-08-24", "mood_score": 4, "notes": "Slept 6 hours."},
        {"entry_date": "2026-08-25", "mood_score": 7, "notes": "Work felt calmer."},
        {"entry_date": "2026-08-26", "mood_score": 6, "notes": "Took a walk."},
        {"entry_date": "2026-08-27", "mood_score": 7, "notes": "Felt supported."},
    ]
    response = provider_responses["supported_facts_response"]

    assert validate_basic_groundedness(response, entries) == response


def test_unsupported_number_is_rejected(provider_responses):
    entries = [
        {"entry_date": "2026-08-24", "mood_score": 4, "notes": "Slept well."}
    ]

    with pytest.raises(AIGroundednessError, match="unsupported number"):
        validate_basic_groundedness(
            provider_responses["unsupported_number_response"], entries
        )


def test_unsupported_date_is_rejected(provider_responses):
    entries = [
        {"entry_date": "2026-08-24", "mood_score": 4, "notes": "Felt tired."}
    ]

    with pytest.raises(AIGroundednessError, match="unsupported date"):
        validate_basic_groundedness(
            provider_responses["unsupported_date_response"], entries
        )


def test_summary_without_concrete_facts_is_accepted(provider_responses):
    entries = [
        {"entry_date": "2026-08-24", "mood_score": 4, "notes": "Felt tired."}
    ]
    response = provider_responses["abstract_grounded_response"]

    assert validate_basic_groundedness(response, entries) == response
