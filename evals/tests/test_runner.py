"""Tests for the offline and live evaluation command-line runner."""

import json
import pytest

import evals.run_evals as runner
from evals.run_evals import make_report, make_summary, run_cases, write_report


def _case(case_id="case_one", behavior="generate"):
    entries = [
        {"entry_date": "2026-08-03", "mood_score": 5, "notes": "A steady day."},
        {"entry_date": "2026-08-05", "mood_score": 6, "notes": "Work went well."},
        {"entry_date": "2026-08-07", "mood_score": 5, "notes": "Felt tired."},
        {"entry_date": "2026-08-09", "mood_score": 6, "notes": "Rested."},
    ]
    if behavior == "reject_insufficient_data":
        entries = entries[:3]
    return {
        "id": case_id,
        "category": "normal",
        "expected_behavior": behavior,
        "journal_entries": entries,
    }


def _candidate():
    return {
        "summary": "The week was generally steady.",
        "self_care_tips": ["Take breaks.", "Rest regularly.", "Keep journaling."],
    }


def _dataset():
    return {
        "dataset_version": "1.0",
        "cases": [
            _case(),
        ],
    }


def _rubric():
    return {
        "rubric_version": "1.0",
    }


## Write one JSON object to a temporary test file.
def _write_json(path, value):
    path.write_text(
        json.dumps(value),
        encoding="utf-8",
    )
    return path


## Create temporary dataset and rubric files for CLI tests.
def _asset_paths(tmp_path):
    dataset_path = _write_json(
        tmp_path / "dataset.json",
        _dataset(),
    )
    rubric_path = _write_json(
        tmp_path / "rubric.json",
        _rubric(),
    )

    return dataset_path, rubric_path


## Return one fake result from run_live_evaluation().
def _live_result(passed=True):
    return {
        "dataset_version": "1.0",
        "rubric_version": "1.0",
        "mode": "live",
        "generation_model": "generation-model",
        "judge_model": "judge-model",
        "summary": {
            "total_cases": 1,
            "passed_cases": 1 if passed else 0,
            "failed_cases": 0 if passed else 1,
            "pass_rate": 1.0 if passed else 0.0,
            "required_pass_rate": 0.8,
            "passed": passed,
        },
        "cases": [
            {
                "case_id": "case_one",
                "passed": passed,
                "rubric_result": {
                    "passed": passed,
                    "average_score": 5.0 if passed else 2.0,
                    "failures": (
                        []
                        if passed
                        else ["Average score is below the threshold."]
                    ),
                },
                "error": None,
            }
        ],
    }


## Verify that a candidate fixture is matched to its dataset case.
def test_case_matching():
    dataset = {"cases": [_case()]}

    results = run_cases(dataset, {"case_one": _candidate()})

    assert results[0]["case_id"] == "case_one"
    assert results[0]["passed"] is True


## Verify that a missing fixture candidate fails clearly.
def test_missing_candidate():
    results = run_cases({"cases": [_case()]}, {})

    assert results[0]["passed"] is False
    assert results[0]["checks"]["candidate"]["status"] == "failed"


## Verify that an insufficient-data case is handled without a candidate.
def test_insufficient_case():
    case = _case("too_short", "reject_insufficient_data")

    results = run_cases({"cases": [case]}, {})

    assert results[0]["passed"] is True
    assert results[0]["checks"]["minimum_entries"]["status"] == "passed"


## Verify fixture summary counts and pass rate.
def test_summary_counts():
    summary = make_summary([{"passed": True}, {"passed": True}, {"passed": False}])

    assert summary == {
        "total_cases": 3,
        "passed_cases": 2,
        "failed_cases": 1,
        "pass_rate": 2 / 3,
    }


## Verify that a fixture report is written as valid JSON.
def test_report_write(tmp_path):
    dataset = {"dataset_version": "1.0"}
    rubric = {"rubric_version": "1.0"}
    results = [{"case_id": "one", "passed": True, "checks": {}}]
    report = make_report(dataset, rubric, results)
    output_path = tmp_path / "report.json"

    write_report(report, output_path)

    saved = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved["summary"]["passed_cases"] == 1
    assert saved["run_metadata"]["deterministic_only"] is True


## Verify that fixtures remain the default and never enter live evaluation.
def test_fixture_default(tmp_path, monkeypatch):
    dataset_path, rubric_path = _asset_paths(tmp_path)
    candidates_path = _write_json(
        tmp_path / "candidates.json",
        {"case_one": _candidate()},
    )
    report_path = tmp_path / "fixture-report.json"

    def must_not_run(**kwargs):
        pytest.fail(
            "Default fixtures mode must not run live evaluation."
        )

    monkeypatch.setattr(
        runner,
        "run_live_evaluation",
        must_not_run,
    )

    exit_code = runner.main([
        "--dataset",
        str(dataset_path),
        "--rubric",
        str(rubric_path),
        "--candidates",
        str(candidates_path),
        "--report",
        str(report_path),
    ])

    saved = json.loads(report_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert saved["run_metadata"]["mode"] == "fixtures"
    assert saved["run_metadata"]["deterministic_only"] is True


## Verify that live mode rejects deterministic-only execution.
def test_live_mode_conflict(tmp_path):
    dataset_path, rubric_path = _asset_paths(tmp_path)

    with pytest.raises(SystemExit) as caught:
        runner.main([
            "--mode",
            "live",
            "--deterministic-only",
            "--dataset",
            str(dataset_path),
            "--rubric",
            str(rubric_path),
        ])

    assert caught.value.code == 2


## Verify that live mode requires a generation model.
def test_generation_model_required(tmp_path):
    dataset_path, rubric_path = _asset_paths(tmp_path)

    with pytest.raises(SystemExit) as caught:
        runner.main([
            "--mode",
            "live",
            "--dataset",
            str(dataset_path),
            "--rubric",
            str(rubric_path),
        ])

    assert caught.value.code == 2


## Verify that live mode requires a judge model.
def test_judge_model_required(tmp_path):
    dataset_path, rubric_path = _asset_paths(tmp_path)

    with pytest.raises(SystemExit) as caught:
        runner.main([
            "--mode",
            "live",
            "--generation-model",
            "generation-model",
            "--dataset",
            str(dataset_path),
            "--rubric",
            str(rubric_path),
        ])

    assert caught.value.code == 2


## Verify that live mode requires an API key.
def test_api_key_required(tmp_path, monkeypatch):
    dataset_path, rubric_path = _asset_paths(tmp_path)

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(SystemExit) as caught:
        runner.main([
            "--mode",
            "live",
            "--generation-model",
            "generation-model",
            "--judge-model",
            "judge-model",
            "--dataset",
            str(dataset_path),
            "--rubric",
            str(rubric_path),
        ])

    assert caught.value.code == 2


## Verify live routing, report output, and pass/fail exit codes.
@pytest.mark.parametrize(
    ("evaluation_passed", "expected_exit_code"),
    [
        (True, 0),
        (False, 1),
    ],
)
def test_live_run(
    tmp_path,
    monkeypatch,
    evaluation_passed,
    expected_exit_code,
):
    dataset_path, rubric_path = _asset_paths(tmp_path)
    report_path = tmp_path / "live-report.json"

    fake_client = object()
    captured = {}

    def fake_openai(api_key):
        captured["api_key"] = api_key
        return fake_client

    def fake_live_evaluation(**kwargs):
        captured["live_arguments"] = kwargs
        return _live_result(passed=evaluation_passed)

    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")

    import openai

    monkeypatch.setattr(openai, "OpenAI", fake_openai)
    monkeypatch.setattr(
        runner,
        "run_live_evaluation",
        fake_live_evaluation,
    )

    exit_code = runner.main([
        "--mode",
        "live",
        "--generation-model",
        "generation-model",
        "--judge-model",
        "judge-model",
        "--dataset",
        str(dataset_path),
        "--rubric",
        str(rubric_path),
        "--report",
        str(report_path),
    ])

    saved = json.loads(report_path.read_text(encoding="utf-8"))
    live_arguments = captured["live_arguments"]

    assert exit_code == expected_exit_code
    assert captured["api_key"] == "test-api-key"
    assert live_arguments["client"] is fake_client
    assert live_arguments["generation_model"] == "generation-model"
    assert live_arguments["judge_model"] == "judge-model"
    assert saved["run_metadata"]["mode"] == "live"
    assert saved["run_metadata"]["deterministic_only"] is False
    assert saved["summary"]["passed"] is evaluation_passed
