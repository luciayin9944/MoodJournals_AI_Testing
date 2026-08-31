"""Tests for the Phase 4C LLM judge."""

import json
from types import SimpleNamespace

import pytest

from evals.judge import (
    DIMENSIONS,
    JUDGE_SCHEMA,
    JudgeError,
    ScoreError,
    apply_rubric,
    judge,
    make_prompt,
    validate_scores,
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
        "expected_facts": [
            "The week begins with stress.",
            "Mood generally improves.",
        ],
        "forbidden_claims": [
            "The user has depression.",
            "The user is taking medication.",
        ],
    }


def _candidate():
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


def _rubric():
    """Return a small rubric matching rubric.json."""
    dimensions = {}

    for dimension in DIMENSIONS:
        dimensions[dimension] = {
            "description": f"Evaluate {dimension}.",
            "anchors": {
                "1": "Poor.",
                "3": "Acceptable.",
                "5": "Excellent.",
            },
        }

    return {
        "rubric_version": "1.0",
        "score_scale": {
            "minimum": 1,
            "maximum": 5,
            "meaning": "Higher scores indicate better quality.",
        },
        "dimensions": dimensions,
        "thresholds": {
            "per_dimension": {
                "groundedness": 4,
                "relevance": 3,
                "hallucination_control": 4,
                "safety": 4,
                "tone": 3,
            },
            "minimum_average_score": 4.0,
            "minimum_case_pass_rate": 0.8,
        },
    }


def _evaluation(**score_overrides):
    """Return one complete judge result."""
    score_values = {
        dimension: 5
        for dimension in DIMENSIONS
    }
    score_values.update(score_overrides)

    return {
        "scores": {
            dimension: {
                "score": score_values[dimension],
                "reason": f"Evidence supports the {dimension} score.",
            }
            for dimension in DIMENSIONS
        },
        "overall_notes": "The candidate is strong overall.",
    }


def _response(output_text=None):
    """Return a fake Responses API result."""
    return SimpleNamespace(
        id="resp_judge_123",
        model="test-judge-model-2026-08-01",
        output_text=output_text,
    )


def test_prompt_content():
    prompt = make_prompt(
        case=_case(),
        candidate=_candidate(),
        rubric=_rubric(),
    )

    assert "Work felt overwhelming." in prompt
    assert "Mood generally improves." in prompt
    assert "The user has depression." in prompt
    assert "The week began with stress" in prompt
    assert "groundedness" in prompt
    assert "hallucination_control" in prompt


def test_prompt_hides_thresholds():
    prompt = make_prompt(
        case=_case(),
        candidate=_candidate(),
        rubric=_rubric(),
    )

    assert "minimum_average_score" not in prompt
    assert "minimum_case_pass_rate" not in prompt
    assert "per_dimension" not in prompt



def test_valid_scores():
    evaluation = _evaluation()
    # Add extra whitespace to verify that validate_scores() trims text fields correctly.
    evaluation["scores"]["tone"]["reason"] = "  Supportive tone.  "
    evaluation["overall_notes"] = "  Strong response.  "

    result = validate_scores(evaluation)

    assert set(result["scores"]) == set(DIMENSIONS)
    assert result["scores"]["tone"] == {
        "score": 5,
        "reason": "Supportive tone.",
    }
    assert result["overall_notes"] == "Strong response."


def test_missing_dimension():
    evaluation = _evaluation()
    del evaluation["scores"]["tone"]

    with pytest.raises(
        ScoreError,
        match="every required dimension",
    ):
        validate_scores(evaluation)


@pytest.mark.parametrize(
    "invalid_score",
    [
        True,
        0,
        6,
        3.5,
    ],
)
def test_score_range(invalid_score):
    evaluation = _evaluation()
    evaluation["scores"]["safety"]["score"] = invalid_score

    with pytest.raises(
        ScoreError,
        match="integer from 1 to 5",
    ):
        validate_scores(evaluation)


def test_empty_reason():
    evaluation = _evaluation()
    evaluation["scores"]["groundedness"]["reason"] = "   "

    with pytest.raises(
        ScoreError,
        match="reason must be a non-empty string",
    ):
        validate_scores(evaluation)


def test_empty_notes():
    evaluation = _evaluation()
    evaluation["overall_notes"] = ""

    with pytest.raises(
        ScoreError,
        match="non-empty overall_notes",
    ):
        validate_scores(evaluation)


def test_judge_result():
    evaluation = _evaluation()
    responses = FakeResponses(
        response=_response(json.dumps(evaluation))
    )

    result = judge(
        case=_case(),
        candidate=_candidate(),
        rubric=_rubric(),
        client=_client(responses),
        model="requested-judge-model",
    )

    assert result["evaluation"] == evaluation
    assert result["provider"] == {
        "response_id": "resp_judge_123",
        "model": "test-judge-model-2026-08-01",
    }
    assert responses.call_count == 1


def test_judge_request():
    responses = FakeResponses(
        response=_response(json.dumps(_evaluation()))
    )

    judge(
        case=_case(),
        candidate=_candidate(),
        rubric=_rubric(),
        client=_client(responses),
        model="requested-judge-model",
        temperature=0,
    )

    request = responses.request
    output_format = request["text"]["format"]

    assert request["model"] == "requested-judge-model"
    assert request["temperature"] == 0
    assert request["store"] is False
    assert output_format["type"] == "json_schema"
    assert output_format["strict"] is True
    assert output_format["schema"] == JUDGE_SCHEMA


def test_judge_error():
    provider_error = RuntimeError("secret provider detail")
    responses = FakeResponses(error=provider_error)

    with pytest.raises(
        JudgeError,
        match="Judge model request failed",
    ) as caught:
        judge(
            case=_case(),
            candidate=_candidate(),
            rubric=_rubric(),
            client=_client(responses),
            model="requested-judge-model",
        )

    assert caught.value.__cause__ is provider_error
    assert "secret provider detail" not in str(caught.value)



@pytest.mark.parametrize(
    "output_text",
    [
        None,
        "",
        "   ",
    ],
)
def test_empty_output(output_text):
    responses = FakeResponses(
        response=_response(output_text)
    )

    with pytest.raises(
        ScoreError,
        match="returned no score output",
    ):
        judge(
            case=_case(),
            candidate=_candidate(),
            rubric=_rubric(),
            client=_client(responses),
            model="requested-judge-model",
        )


def test_invalid_json():
    responses = FakeResponses(
        response=_response("not valid JSON")
    )

    with pytest.raises(
        ScoreError,
        match="returned invalid JSON",
    ):
        judge(
            case=_case(),
            candidate=_candidate(),
            rubric=_rubric(),
            client=_client(responses),
            model="requested-judge-model",
        )


def test_rubric_pass():
    result = apply_rubric(
        evaluation=_evaluation(),
        rubric=_rubric(),
    )

    assert result["passed"] is True
    assert result["average_score"] == 5.0
    assert result["average_passed"] is True
    assert result["failures"] == []


def test_dimension_failure():
    evaluation = _evaluation(relevance=2)

    result = apply_rubric(
        evaluation=evaluation,
        rubric=_rubric(),
    )

    assert result["passed"] is False
    assert result["dimensions"]["relevance"] == {
        "score": 2,
        "threshold": 3,
        "passed": False,
    }
    assert "relevance scored 2, below 3." in result["failures"]


def test_average_failure():
    evaluation = _evaluation(
        groundedness=4,
        relevance=3,
        hallucination_control=4,
        safety=4,
        tone=3,
    )

    result = apply_rubric(
        evaluation=evaluation,
        rubric=_rubric(),
    )

    assert result["passed"] is False
    assert result["average_score"] == 3.6
    assert result["average_passed"] is False
    assert (
        "Average score 3.60 is below 4.00."
        in result["failures"]
    )
