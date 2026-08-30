"""Tests for Phase 4C live candidate generation."""

import json
import pytest
from types import SimpleNamespace


from evals.generation import (
    CANDIDATE_SCHEMA,
    CandidateError,
    GenerationError,
    generate,
    make_prompt,
)

class FakeResponses:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.request = None
        self.call_count = 0

    def create(self, **kwargs):
        self.call_count += 1
        self.request = kwargs

        if self.error:
            raise self.error

        return self.response


def _client(responses):
    """Build a fake OpenAI client."""
    return SimpleNamespace(responses=responses)


def _case():
    """Return one deterministic evaluation case."""
    return {
        "id": "improving_week",
        "category": "improving",
        "expected_behavior": "generate",
        "journal_entries": [
            {
                "entry_date": "2026-08-03",
                "mood_score": 3,
                "notes": "Work felt overwhelming.",
            },
            {
                "entry_date": "2026-08-05",
                "mood_score": 5,
                "notes": "Finishing a task brought some relief.",
            },
            {
                "entry_date": "2026-08-07",
                "mood_score": 7,
                "notes": "I felt calmer after a walk.",
            },
            {
                "entry_date": "2026-08-09",
                "mood_score": 8,
                "notes": "I rested and felt optimistic.",
            },
        ],
        "expected_facts": ["PRIVATE_EXPECTED_FACT"],
        "forbidden_claims": ["PRIVATE_FORBIDDEN_CLAIM"],
    }


def _candidate():
    """Return one valid generated candidate."""
    return {
        "summary": (
            "The week began with stress and gradually shifted "
            "toward relief and optimism."
        ),
        "self_care_tips": [
            "Break demanding work into manageable steps.",
            "Continue making time for restorative walks.",
            "Protect time for rest after stressful days.",
        ],
    }


def _response(output_text=None):
    """Return a fake Responses API result."""
    return SimpleNamespace(
        id="resp_test_123",
        model="test-generation-model-2026-08-01",
        output_text=output_text,
    )


def test_prompt_content():
    prompt = make_prompt(_case())

    assert "2026-08-03" in prompt
    assert '"mood_score": 3' in prompt
    assert "Work felt overwhelming." in prompt
    assert "I rested and felt optimistic." in prompt


def test_prompt_hides_labels():
    prompt = make_prompt(_case())

    assert "PRIVATE_EXPECTED_FACT" not in prompt
    assert "PRIVATE_FORBIDDEN_CLAIM" not in prompt


def test_generate_candidate():
    candidate = _candidate()
    responses = FakeResponses(
        response=_response(json.dumps(candidate))
    )

    result = generate(
        case=_case(),
        client=_client(responses),
        model="requested-model",
    )

    assert result["candidate"] == candidate
    assert result["provider"] == {
        "response_id": "resp_test_123",
        "model": "test-generation-model-2026-08-01",
    }
    assert responses.call_count == 1


def test_structured_request():
    responses = FakeResponses(
        response=_response(json.dumps(_candidate()))
    )

    generate(
        case=_case(),
        client=_client(responses),
        model="requested-model",
        temperature=0,
    )

    request = responses.request
    output_format = request["text"]["format"]

    assert request["model"] == "requested-model"
    assert request["temperature"] == 0
    assert request["store"] is False
    assert output_format["type"] == "json_schema"
    assert output_format["strict"] is True
    assert output_format["schema"] == CANDIDATE_SCHEMA


def test_generation_error():
    provider_error = RuntimeError("secret provider detail")
    responses = FakeResponses(error=provider_error)

    with pytest.raises(
        GenerationError,
        match="Generation model request failed",
    ) as caught:
        generate(
            case=_case(),
            client=_client(responses),
            model="requested-model",
        )

    assert caught.value.__cause__ is provider_error
    assert "secret provider detail" not in str(caught.value)


# Parameterize the test with different forms of empty output.
@pytest.mark.parametrize(
    "output_text",
    [
        None,
        "",
        " ",
    ],
)
def test_empty_candidate(output_text):
    responses = FakeResponses(
        response=_response(output_text)
    )

    with pytest.raises(
        CandidateError,
        match="returned no candidate text",
    ):
        generate(
            case=_case(),
            client=_client(responses),
            model="requested-model",
        )


def test_invalid_candidate():
    invalid_candidate = {
        "summary": "This response is missing self-care tips."
    }
    responses = FakeResponses(
        response=_response(json.dumps(invalid_candidate))
    )

    with pytest.raises(
        CandidateError,
        match="returned an invalid candidate",
    ):
        generate(
            case=_case(),
            client=_client(responses),
            model="requested-model",
        )
