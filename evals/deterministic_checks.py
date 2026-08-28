"""Adapters that apply the existing deterministic AI validators to eval cases."""

import json

from server.ai_safety import (
    AIContentSafetyError,
    AIGroundednessError,
    validate_ai_content_safety,
    validate_basic_groundedness,
)
from server.ai_validation import (
    AIResponseValidationError,
    parse_and_validate_ai_response,
)


def _check(status, error=None):
    result = {"status": status}
    if error:
        result["error"] = error
    return result


def check_entries(case):
    """Evaluate a case that should stop before AI generation."""
    passed = len(case["journal_entries"]) < 4
    return {
        "case_id": case["id"],
        "category": case["category"],
        "expected_behavior": case["expected_behavior"],
        "passed": passed,
        "checks": {
            "minimum_entries": _check("passed" if passed else "failed")
        },
    }


def run_checks(case, candidate):
    """Run contract first, then independently run safety and groundedness."""
    result = {
        "case_id": case["id"],
        "category": case["category"],
        "expected_behavior": case["expected_behavior"],
        "passed": False,
        "checks": {},
    }

    raw_candidate = candidate if isinstance(candidate, str) else json.dumps(candidate)
    try:
        validated = parse_and_validate_ai_response(raw_candidate)
        result["checks"]["contract"] = _check("passed")
    except AIResponseValidationError as error:
        result["checks"]["contract"] = _check("failed", str(error))
        result["checks"]["safety"] = _check(
            "not_run", "Contract validation failed."
        )
        result["checks"]["basic_groundedness"] = _check(
            "not_run", "Contract validation failed."
        )
        return result

    try:
        validate_ai_content_safety(validated)
        result["checks"]["safety"] = _check("passed")
    except AIContentSafetyError as error:
        result["checks"]["safety"] = _check("failed", str(error))

    try:
        validate_basic_groundedness(validated, case["journal_entries"])
        result["checks"]["basic_groundedness"] = _check("passed")
    except AIGroundednessError as error:
        result["checks"]["basic_groundedness"] = _check("failed", str(error))

    result["passed"] = all(
        check["status"] == "passed" for check in result["checks"].values()
    )
    return result
