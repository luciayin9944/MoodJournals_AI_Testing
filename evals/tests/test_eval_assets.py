import json
from datetime import date
from pathlib import Path


EVALS_DIR = Path(__file__).parents[1]
DATASET_PATH = EVALS_DIR / "dataset.json"
RUBRIC_PATH = EVALS_DIR / "rubric.json"

REQUIRED_CATEGORIES = {
    "normal",
    "improving",
    "declining",
    "mixed",
    "conflicting",
    "limited_data",
    "extreme",
    "hallucination_trap",
    "safety_sensitive",
    "missing_entries",
}
REQUIRED_DIMENSIONS = {
    "groundedness",
    "relevance",
    "hallucination_control",
    "safety",
    "tone",
}


def _load_json(path):
    with path.open(encoding="utf-8") as source_file:
        return json.load(source_file)


def test_dataset_size_and_unique_ids():
    dataset = _load_json(DATASET_PATH)
    cases = dataset["cases"]
    case_ids = [case["id"] for case in cases]

    assert dataset["dataset_version"] == "1.0"
    assert 10 <= len(cases) <= 20
    assert len(case_ids) == len(set(case_ids))


def test_required_categories():
    cases = _load_json(DATASET_PATH)["cases"]
    categories = {case["category"] for case in cases}

    assert REQUIRED_CATEGORIES <= categories


def test_case_labels():
    cases = _load_json(DATASET_PATH)["cases"]

    for case in cases:
        assert case["description"].strip()
        assert case["expected_facts"]
        assert case["forbidden_claims"]
        assert all(fact.strip() for fact in case["expected_facts"])
        assert all(claim.strip() for claim in case["forbidden_claims"])


def test_journal_entry_fields():
    cases = _load_json(DATASET_PATH)["cases"]

    for case in cases:
        entry_dates = []
        for entry in case["journal_entries"]:
            entry_dates.append(date.fromisoformat(entry["entry_date"]))
            assert isinstance(entry["mood_score"], int)
            assert 1 <= entry["mood_score"] <= 10
            assert isinstance(entry["notes"], str)
            assert entry["notes"].strip()

        assert entry_dates == sorted(entry_dates)
        assert len(entry_dates) == len(set(entry_dates))


def test_entry_count_behavior():
    cases = _load_json(DATASET_PATH)["cases"]

    for case in cases:
        if case["expected_behavior"] == "generate":
            assert len(case["journal_entries"]) >= 4
        else:
            assert case["expected_behavior"] == "reject_insufficient_data"
            assert len(case["journal_entries"]) < 4


def test_rubric_dimensions_and_anchors():
    rubric = _load_json(RUBRIC_PATH)
    dimensions = rubric["dimensions"]

    assert rubric["rubric_version"] == "1.0"
    assert set(dimensions) == REQUIRED_DIMENSIONS
    for definition in dimensions.values():
        assert definition["description"].strip()
        assert set(definition["anchors"]) == {"1", "3", "5"}
        assert all(anchor.strip() for anchor in definition["anchors"].values())


def test_rubric_thresholds():
    rubric = _load_json(RUBRIC_PATH)
    minimum = rubric["score_scale"]["minimum"]
    maximum = rubric["score_scale"]["maximum"]
    thresholds = rubric["thresholds"]

    assert minimum == 1
    assert maximum == 5
    assert set(thresholds["per_dimension"]) == REQUIRED_DIMENSIONS
    assert all(
        minimum <= score <= maximum
        for score in thresholds["per_dimension"].values()
    )
    assert minimum <= thresholds["minimum_average_score"] <= maximum
    assert 0 < thresholds["minimum_case_pass_rate"] <= 1
