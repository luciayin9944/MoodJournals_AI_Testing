import json

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


def test_case_matching():
    dataset = {"cases": [_case()]}

    results = run_cases(dataset, {"case_one": _candidate()})

    assert results[0]["case_id"] == "case_one"
    assert results[0]["passed"] is True


def test_missing_candidate():
    results = run_cases({"cases": [_case()]}, {})

    assert results[0]["passed"] is False
    assert results[0]["checks"]["candidate"]["status"] == "failed"


def test_insufficient_case():
    case = _case("too_short", "reject_insufficient_data")

    results = run_cases({"cases": [case]}, {})

    assert results[0]["passed"] is True
    assert results[0]["checks"]["minimum_entries"]["status"] == "passed"


def test_summary_counts():
    summary = make_summary([{"passed": True}, {"passed": True}, {"passed": False}])

    assert summary == {
        "total_cases": 3,
        "passed_cases": 2,
        "failed_cases": 1,
        "pass_rate": 2 / 3,
    }


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
