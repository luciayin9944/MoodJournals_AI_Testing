"""Tests for Phase 4C live evaluation orchestration."""

import pytest

import evals.live_eval as live_eval
from evals.generation import GenerationError
from evals.judge import JudgeError


def _case(expected_behavior="generate"):
    return {
        "id": "improving_week",
        "category": "improving",
        "expected_behavior": expected_behavior,
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
            "The week began with stress and gradually improved "
            "toward relief and optimism."
        ),
        "self_care_tips": [
            "Break demanding work into manageable steps.",
            "Continue making time for restorative walks.",
            "Protect time for rest after stressful days.",
        ],
    }


def _rubric(minimum_case_pass_rate=0.8):
    return {
        "rubric_version": "1.0",
        "thresholds": {
            "minimum_case_pass_rate": minimum_case_pass_rate,
        },
    }


def _generation_result():
    return {
        "candidate": _candidate(),
        "provider": {
            "response_id": "generation-response-123",
            "model": "actual-generation-model",
        },
    }


def _deterministic_result(passed=True):
    return {
        "case_id": "improving_week",
        "category": "improving",
        "expected_behavior": "generate",
        "passed": passed,
        "checks": {
            "contract": {
                "status": "passed" if passed else "failed",
            },
            "safety": {
                "status": "passed",
            },
            "basic_groundedness": {
                "status": "passed",
            },
        },
    }


def _evaluation():
    return {
        "scores": {
            "groundedness": {
                "score": 5,
                "reason": "The summary is supported by the entries.",
            },
            "relevance": {
                "score": 5,
                "reason": "The response addresses the weekly pattern.",
            },
            "hallucination_control": {
                "score": 5,
                "reason": "No unsupported facts were introduced.",
            },
            "safety": {
                "score": 5,
                "reason": "The suggestions are safe and supportive.",
            },
            "tone": {
                "score": 5,
                "reason": "The tone is respectful and empathetic.",
            },
        },
        "overall_notes": "The candidate is strong overall.",
    }


def _judge_result():
    return {
        "evaluation": _evaluation(),
        "provider": {
            "response_id": "judge-response-123",
            "model": "actual-judge-model",
        },
    }


def _rubric_result(passed=True):
    return {
        "passed": passed,
        "average_score": 5.0 if passed else 3.0,
        "minimum_average": 4.0,
        "average_passed": passed,
        "dimensions": {},
        "failures": [] if passed else ["A score was below its threshold."],
    }


## Verify that a normal generation case completes every evaluation stage.
def test_generation_case(monkeypatch):
    monkeypatch.setattr(
        live_eval,
        "generate",
        lambda **kwargs: _generation_result(),
    )
    monkeypatch.setattr(
        live_eval,
        "run_checks",
        lambda case, candidate: _deterministic_result(),
    )
    monkeypatch.setattr(
        live_eval,
        "judge",
        lambda **kwargs: _judge_result(),
    )
    monkeypatch.setattr(
        live_eval,
        "apply_rubric",
        lambda evaluation, rubric: _rubric_result(),
    )

    result = live_eval.evaluate_generation_case(
        case=_case(),
        rubric=_rubric(),
        client=object(),
        generation_model="requested-generation-model",
        judge_model="requested-judge-model",
    )

    assert result["passed"] is True
    assert result["candidate"] == _candidate()
    assert result["generation_provider"]["response_id"] == (
        "generation-response-123"
    )
    assert result["deterministic"]["passed"] is True
    assert result["semantic"] == _evaluation()
    assert result["judge_provider"]["response_id"] == (
        "judge-response-123"
    )
    assert result["rubric_result"]["passed"] is True
    assert result["error"] is None


## Verify that deterministic failure makes the case fail.
def test_deterministic_failure(monkeypatch):
    monkeypatch.setattr(
        live_eval,
        "generate",
        lambda **kwargs: _generation_result(),
    )
    monkeypatch.setattr(
        live_eval,
        "run_checks",
        lambda case, candidate: _deterministic_result(passed=False),
    )
    monkeypatch.setattr(
        live_eval,
        "judge",
        lambda **kwargs: _judge_result(),
    )
    monkeypatch.setattr(
        live_eval,
        "apply_rubric",
        lambda evaluation, rubric: _rubric_result(),
    )

    result = live_eval.evaluate_generation_case(
        case=_case(),
        rubric=_rubric(),
        client=object(),
        generation_model="generation-model",
        judge_model="judge-model",
    )

    assert result["deterministic"]["passed"] is False
    assert result["rubric_result"]["passed"] is True
    assert result["passed"] is False


## Verify that a failed semantic rubric makes the case fail.
def test_rubric_failure(monkeypatch):
    monkeypatch.setattr(
        live_eval,
        "generate",
        lambda **kwargs: _generation_result(),
    )
    monkeypatch.setattr(
        live_eval,
        "run_checks",
        lambda case, candidate: _deterministic_result(),
    )
    monkeypatch.setattr(
        live_eval,
        "judge",
        lambda **kwargs: _judge_result(),
    )
    monkeypatch.setattr(
        live_eval,
        "apply_rubric",
        lambda evaluation, rubric: _rubric_result(passed=False),
    )

    result = live_eval.evaluate_generation_case(
        case=_case(),
        rubric=_rubric(),
        client=object(),
        generation_model="generation-model",
        judge_model="judge-model",
    )

    assert result["deterministic"]["passed"] is True
    assert result["rubric_result"]["passed"] is False
    assert result["passed"] is False


## Verify that generation errors are recorded without calling later stages.
def test_generation_error(monkeypatch):
    def fail_generation(**kwargs):
        raise GenerationError("Generation model request failed.")

    def must_not_run(*args, **kwargs):
        pytest.fail("Later evaluation stages must not run.")

    monkeypatch.setattr(
        live_eval,
        "generate",
        fail_generation,
    )
    monkeypatch.setattr(
        live_eval,
        "run_checks",
        must_not_run,
    )
    monkeypatch.setattr(
        live_eval,
        "judge",
        must_not_run,
    )

    result = live_eval.evaluate_generation_case(
        case=_case(),
        rubric=_rubric(),
        client=object(),
        generation_model="generation-model",
        judge_model="judge-model",
    )

    assert result["passed"] is False
    assert result["candidate"] is None
    assert result["deterministic"] is None
    assert result["semantic"] is None
    assert result["error"] == {
        "stage": "generation",
        "message": "Generation model request failed.",
    }


## Verify that judge errors preserve earlier deterministic results.
def test_judge_error(monkeypatch):
    def fail_judge(**kwargs):
        raise JudgeError("Judge model request failed.")

    monkeypatch.setattr(
        live_eval,
        "generate",
        lambda **kwargs: _generation_result(),
    )
    monkeypatch.setattr(
        live_eval,
        "run_checks",
        lambda case, candidate: _deterministic_result(),
    )
    monkeypatch.setattr(
        live_eval,
        "judge",
        fail_judge,
    )

    result = live_eval.evaluate_generation_case(
        case=_case(),
        rubric=_rubric(),
        client=object(),
        generation_model="generation-model",
        judge_model="judge-model",
    )

    assert result["passed"] is False
    assert result["candidate"] == _candidate()
    assert result["deterministic"]["passed"] is True
    assert result["semantic"] is None
    assert result["rubric_result"] is None
    assert result["error"] == {
        "stage": "judge",
        "message": "Judge model request failed.",
    }


## Verify that insufficient-data cases never call generation or judge models.
def test_rejection_case(monkeypatch):
    case = _case(expected_behavior="reject_insufficient_data")
    case["journal_entries"] = case["journal_entries"][:3]

    def must_not_run(*args, **kwargs):
        pytest.fail("A rejection case must not call an AI model.")

    monkeypatch.setattr(
        live_eval,
        "generate",
        must_not_run,
    )
    monkeypatch.setattr(
        live_eval,
        "judge",
        must_not_run,
    )

    result = live_eval.evaluate_case(
        case=case,
        rubric=_rubric(),
        client=object(),
        generation_model="generation-model",
        judge_model="judge-model",
    )

    assert result["passed"] is True
    assert result["candidate"] is None
    assert result["deterministic"]["checks"]["minimum_entries"][
        "status"
    ] == "passed"
    assert result["semantic"] is None
    assert result["error"] is None


## Verify that unsupported expected behavior is reported clearly.
def test_unknown_behavior():
    case = _case(expected_behavior="unknown_behavior")

    result = live_eval.evaluate_case(
        case=case,
        rubric=_rubric(),
        client=object(),
        generation_model="generation-model",
        judge_model="judge-model",
    )

    assert result["passed"] is False
    assert result["error"]["stage"] == "case_validation"
    assert "unknown_behavior" in result["error"]["message"]


## Verify the dataset-level pass-rate calculation.
@pytest.mark.parametrize(
    (
        "case_results",
        "required_rate",
        "expected_passed",
    ),
    [
        (
            [
                {"passed": True},
                {"passed": True},
                {"passed": False},
            ],
            0.6,
            True,
        ),
        (
            [
                {"passed": True},
                {"passed": False},
                {"passed": False},
            ],
            0.8,
            False,
        ),
    ],
)
def test_summary(case_results, required_rate, expected_passed):
    result = live_eval.summarize(
        results=case_results,
        rubric=_rubric(required_rate),
    )

    passed_cases = sum(
        1 for case_result in case_results
        if case_result["passed"]
    )

    assert result["total_cases"] == 3
    assert result["passed_cases"] == passed_cases
    assert result["failed_cases"] == 3 - passed_cases
    assert result["required_pass_rate"] == required_rate
    assert result["passed"] is expected_passed


## Verify that the complete runner returns metadata, cases, and summary.
def test_live_run(monkeypatch):
    dataset = {
        "dataset_version": "1.0",
        "cases": [
            _case(),
            {
                **_case(),
                "id": "second_case",
            },
        ],
    }

    returned_results = [
        {
            "case_id": "improving_week",
            "passed": True,
        },
        {
            "case_id": "second_case",
            "passed": False,
        },
    ]

    call_count = 0

    def fake_evaluate_case(**kwargs):
        nonlocal call_count
        result = returned_results[call_count]
        call_count += 1
        return result

    monkeypatch.setattr(
        live_eval,
        "evaluate_case",
        fake_evaluate_case,
    )

    result = live_eval.run_live_evaluation(
        dataset=dataset,
        rubric=_rubric(minimum_case_pass_rate=0.5),
        client=object(),
        generation_model="generation-model",
        judge_model="judge-model",
    )

    assert call_count == 2
    assert result["dataset_version"] == "1.0"
    assert result["rubric_version"] == "1.0"
    assert result["mode"] == "live"
    assert result["generation_model"] == "generation-model"
    assert result["judge_model"] == "judge-model"
    assert result["cases"] == returned_results
    assert result["summary"]["pass_rate"] == 0.5
    assert result["summary"]["passed"] is True