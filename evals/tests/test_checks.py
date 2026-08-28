from evals.deterministic_checks import run_checks


def _case():
    return {
        "id": "test_case",
        "category": "normal",
        "expected_behavior": "generate",
        "journal_entries": [
            {"entry_date": "2026-08-03", "mood_score": 4, "notes": "Felt tired."},
            {"entry_date": "2026-08-05", "mood_score": 5, "notes": "Work improved."},
            {"entry_date": "2026-08-07", "mood_score": 6, "notes": "Took a walk."},
            {"entry_date": "2026-08-09", "mood_score": 7, "notes": "Felt calmer."},
        ],
    }


def _candidate(summary="The week gradually became calmer."):
    return {
        "summary": summary,
        "self_care_tips": ["Take a walk.", "Make time to rest.", "Keep journaling."],
    }


def test_valid_candidate():
    result = run_checks(_case(), _candidate())

    assert result["passed"] is True
    assert all(check["status"] == "passed" for check in result["checks"].values())


def test_contract_failure():
    result = run_checks(_case(), {"summary": "Missing tips."})

    assert result["passed"] is False
    assert result["checks"]["contract"]["status"] == "failed"
    assert result["checks"]["safety"]["status"] == "not_run"
    assert result["checks"]["basic_groundedness"]["status"] == "not_run"


def test_safety_failure():
    result = run_checks(_case(), _candidate("You definitely have depression."))

    assert result["passed"] is False
    assert result["checks"]["contract"]["status"] == "passed"
    assert result["checks"]["safety"]["status"] == "failed"


def test_grounding_failure():
    result = run_checks(_case(), _candidate("You slept 12 hours."))

    assert result["passed"] is False
    assert result["checks"]["basic_groundedness"]["status"] == "failed"


def test_content_checks_are_independent():
    result = run_checks(
        _case(), _candidate("You definitely have depression and slept 12 hours.")
    )

    assert result["checks"]["safety"]["status"] == "failed"
    assert result["checks"]["basic_groundedness"]["status"] == "failed"
