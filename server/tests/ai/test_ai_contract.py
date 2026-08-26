import json
from pathlib import Path

import pytest

from ai_validation import (
    AIResponseValidationError,
    MAX_SERIALIZED_TIPS_LENGTH,
    MAX_SUMMARY_LENGTH,
    parse_and_validate_ai_response,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "provider_responses.json"


@pytest.fixture(scope="module")
def provider_responses():
    with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


def test_valid_response_is_accepted(provider_responses):
    raw_response = json.dumps(provider_responses["valid_response"])

    result = parse_and_validate_ai_response(raw_response)

    assert result == provider_responses["valid_response"]


def test_summary_and_tips_are_trimmed(provider_responses):
    raw_response = json.dumps(provider_responses["whitespace_response"])

    result = parse_and_validate_ai_response(raw_response)

    assert result["summary"] == "The week became more balanced."
    assert result["self_care_tips"] == [
        "Take a short walk.",
        "Keep a regular sleep routine.",
        "Reflect on one positive moment.",
    ]


def test_standard_json_code_fences_are_accepted(provider_responses):
    for fixture_name in ("json_code_fence", "plain_code_fence"):
        result = parse_and_validate_ai_response(provider_responses[fixture_name])
        assert len(result["self_care_tips"]) == 3


def test_raw_response_must_be_a_string():
    with pytest.raises(AIResponseValidationError, match="must be a string"):
        parse_and_validate_ai_response({"summary": "Not a raw string"})


def test_malformed_json_is_rejected(provider_responses):
    with pytest.raises(AIResponseValidationError, match="valid JSON"):
        parse_and_validate_ai_response(provider_responses["malformed_json"])


def test_top_level_value_must_be_an_object(provider_responses):
    with pytest.raises(AIResponseValidationError, match="JSON object"):
        parse_and_validate_ai_response(provider_responses["top_level_array"])


def test_required_fields_must_be_present(provider_responses):
    for fixture_name, expected_field in (
        ("missing_summary", "summary"),
        ("missing_tips", "self_care_tips"),
    ):
        with pytest.raises(AIResponseValidationError, match=expected_field):
            parse_and_validate_ai_response(
                json.dumps(provider_responses[fixture_name])
            )


def test_summary_must_be_a_non_empty_string(provider_responses):
    for fixture_name in ("empty_summary", "numeric_summary"):
        with pytest.raises(AIResponseValidationError, match="non-empty string"):
            parse_and_validate_ai_response(
                json.dumps(provider_responses[fixture_name])
            )


def test_tips_must_be_a_list(provider_responses):
    with pytest.raises(AIResponseValidationError, match="must be a list"):
        parse_and_validate_ai_response(
            json.dumps(provider_responses["wrong_tips_type"])
        )


def test_tips_must_contain_exactly_three_items(provider_responses):
    for fixture_name in ("two_tips", "four_tips"):
        with pytest.raises(AIResponseValidationError, match="exactly 3"):
            parse_and_validate_ai_response(
                json.dumps(provider_responses[fixture_name])
            )


def test_each_tip_must_be_a_non_empty_string(provider_responses):
    for fixture_name in ("empty_tip", "numeric_tip"):
        with pytest.raises(AIResponseValidationError, match="non-empty string"):
            parse_and_validate_ai_response(
                json.dumps(provider_responses[fixture_name])
            )


def test_summary_and_serialized_tips_length_limits_are_enforced():
    too_long_summary = json.dumps({
        "summary": "s" * (MAX_SUMMARY_LENGTH + 1),
        "self_care_tips": ["Tip one.", "Tip two.", "Tip three."],
    })
    with pytest.raises(AIResponseValidationError, match="summary must not exceed"):
        parse_and_validate_ai_response(too_long_summary)

    long_tip = "t" * MAX_SERIALIZED_TIPS_LENGTH
    too_long_tips = json.dumps({
        "summary": "A valid summary.",
        "self_care_tips": [long_tip, "Tip two.", "Tip three."],
    })
    with pytest.raises(AIResponseValidationError, match="serialized length"):
        parse_and_validate_ai_response(too_long_tips)
