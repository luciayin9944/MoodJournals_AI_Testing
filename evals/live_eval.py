"""Orchestration for Phase 4C live AI evaluations."""

from evals.deterministic_checks import check_entries, run_checks
from evals.generation import GenerationError, generate
from evals.judge import JudgeError, apply_rubric, judge

## Build a consistent result record before an evaluation case runs.
def make_case_result(case):
    return {
        "case_id": case["id"],
        "category": case["category"],
        "expected_behavior": case["expected_behavior"],
        "passed": False,
        "candidate": None,
        "generation_provider": None,
        "deterministic": None,
        "semantic": None,
        "judge_provider": None,
        "rubric_result": None,
        "error": None,
    }

## Evaluate a case that should be rejected because it has insufficient data.
def evaluate_rejection_case(case):
    result = make_case_result(case)
    deterministic_result = check_entries(case)

    result["deterministic"] = deterministic_result
    result["passed"] = deterministic_result["passed"]

    return result

## Generate, validate, and score one case that has enough journal entries.
def evaluate_generation_case(case, rubric, client, generation_model, judge_model, generation_temperature=None, judge_temperature=None):
    result = make_case_result(case)

    try:
        generation_result = generate(
            case=case,
            client=client,
            model=generation_model,
            temperature=generation_temperature,
        )
    except GenerationError as error:
        result["error"] = {
            "stage": "generation",
            "message": str(error),
        }
        return result

    candidate = generation_result["candidate"]

    result["candidate"] = candidate
    result["generation_provider"] = generation_result["provider"]
    result["deterministic"] = run_checks(case, candidate)

    try:
        judge_result = judge(
            case=case,
            candidate=candidate,
            rubric=rubric,
            client=client,
            model=judge_model,
            temperature=judge_temperature,
        )
    except JudgeError as error:
        result["error"] = {
            "stage": "judge",
            "message": str(error),
        }
        return result

    semantic_evaluation = judge_result["evaluation"]
    rubric_result = apply_rubric(
        evaluation=semantic_evaluation,
        rubric=rubric,
    )

    result["semantic"] = semantic_evaluation
    result["judge_provider"] = judge_result["provider"]
    result["rubric_result"] = rubric_result
    result["passed"] = (
        result["deterministic"]["passed"]
        and rubric_result["passed"]
    )
    return result


## Route one dataset case to rejection testing or live generation testing.
def evaluate_case(
    case,
    rubric,
    client,
    generation_model,
    judge_model,
    generation_temperature=None,
    judge_temperature=None,
):
    if case["expected_behavior"] == "reject_insufficient_data":
        return evaluate_rejection_case(case)

    if case["expected_behavior"] == "generate":
        return evaluate_generation_case(
            case=case,
            rubric=rubric,
            client=client,
            generation_model=generation_model,
            judge_model=judge_model,
            generation_temperature=generation_temperature,
            judge_temperature=judge_temperature,
        )

    result = make_case_result(case)
    result["error"] = {
        "stage": "case_validation",
        "message": (
            "Unsupported expected_behavior: "
            f"{case['expected_behavior']}"
        ),
    }
    return result


## Summarize case-level results and apply the required dataset pass rate.
def summarize(results, rubric):
    total_cases = len(results)
    passed_cases = sum(
        1 for result in results
        if result["passed"]
    )
    failed_cases = total_cases - passed_cases

    pass_rate = (
        passed_cases / total_cases
        if total_cases
        else 0.0
    )

    required_pass_rate = rubric["thresholds"][
        "minimum_case_pass_rate"
    ]

    return {
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "failed_cases": failed_cases,
        "pass_rate": pass_rate,
        "required_pass_rate": required_pass_rate,
        "passed": pass_rate >= required_pass_rate,
    }


## Run the complete Phase 4C live evaluation across the dataset.
def run_live_evaluation(
    dataset,
    rubric,
    client,
    generation_model,
    judge_model,
    generation_temperature=None,
    judge_temperature=None,
):
    results = []

    for case in dataset["cases"]:
        result = evaluate_case(
            case=case,
            rubric=rubric,
            client=client,
            generation_model=generation_model,
            judge_model=judge_model,
            generation_temperature=generation_temperature,
            judge_temperature=judge_temperature,
        )
        results.append(result)

    return {
        "dataset_version": dataset["dataset_version"],
        "rubric_version": rubric["rubric_version"],
        "mode": "live",
        "generation_model": generation_model,
        "judge_model": judge_model,
        "summary": summarize(results, rubric),
        "cases": results,
    }