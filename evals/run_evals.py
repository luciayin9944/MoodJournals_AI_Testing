"""Command-line runner for offline and live MoodJournal evaluations."""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from evals.deterministic_checks import check_entries, run_checks
from evals.live_eval import run_live_evaluation


EVALS_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET = EVALS_DIR / "dataset.json"
DEFAULT_RUBRIC = EVALS_DIR / "rubric.json"
DEFAULT_CANDIDATES = (
    EVALS_DIR
    / "fixtures"
    / "candidate_responses.json"
)
REPORTS_DIR = EVALS_DIR / "reports"

## Load a JSON file.
def load_json(path):
    with Path(path).open(encoding="utf-8") as source_file:
        return json.load(source_file)


## Run the existing offline deterministic cases.
def run_cases(dataset, candidates):
    results = []
    for case in dataset["cases"]:
        if case["expected_behavior"] == "reject_insufficient_data":
            results.append(check_entries(case))
            continue

        candidate = candidates.get(case["id"])
        if candidate is None:
            results.append({
                "case_id": case["id"],
                "category": case["category"],
                "expected_behavior": case["expected_behavior"],
                "passed": False,
                "checks": {
                    "candidate": {
                        "status": "failed",
                        "error": "Candidate response is missing.",
                    }
                },
            })
            continue

        results.append(run_checks(case, candidate))

    return results


## Summarize fixture-mode results.
def make_summary(results):
    total = len(results)
    passed = sum(
        1 for result in results
        if result["passed"]
    )
    return {
        "total_cases": total,
        "passed_cases": passed,
        "failed_cases": total - passed,
        "pass_rate": passed / total if total else 0.0,
    }


## Build the existing fixture-mode report.
def make_report(dataset, rubric, results):
    return {
        "run_metadata": {
            "mode": "fixtures",
            "deterministic_only": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "dataset_version": dataset["dataset_version"],
            "rubric_version": rubric["rubric_version"],
        },
        "summary": make_summary(results),
        "cases": results,
    }


## Write a report to a JSON file.
def write_report(report, path):
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(
            report,
            output_file,
            indent=2,
            ensure_ascii=False,
        )
        output_file.write("\n")
    return output_path


## Print the existing fixture-mode report.
def print_report(report, output_path):
    print("MoodJournal Deterministic Evaluation")
    print(f"Dataset version: {report['run_metadata']['dataset_version']}")
    print("Mode: fixtures (deterministic only)\n")

    for result in report["cases"]:
        label = "PASS" if result["passed"] else "FAIL"
        print(f"[{label}] {result['case_id']}")
        for name, check in result["checks"].items():
            print(f"  {name}: {check['status']}")

    summary = report["summary"]
    print("\nSummary")
    print(f"Total: {summary['total_cases']}")
    print(f"Passed: {summary['passed_cases']}")
    print(f"Failed: {summary['failed_cases']}")
    print(f"Pass rate: {summary['pass_rate']:.1%}")
    print(f"Report: {output_path}")


## Print live-evaluation report.
def print_live_report(report, output_path):
    metadata = report["run_metadata"]

    print("MoodJournal Live AI Evaluation")
    print(f"Generation model: {metadata['generation_model']}")
    print(f"Judge model: {metadata['judge_model']}\n")

    for result in report["cases"]:
        label = "PASS" if result["passed"] else "FAIL"
        print(f"[{label}] {result['case_id']}")

        rubric_result = result.get("rubric_result")
        if rubric_result is not None:
            print(
                "  semantic average: "
                f"{rubric_result['average_score']:.2f}"
            )
            for failure in rubric_result["failures"]:
                print(f"  failure: {failure}")

        error = result.get("error")
        if error is not None:
            print(
                f"  error ({error['stage']}): "
                f"{error['message']}"
            )

    summary = report["summary"]
    overall = "PASS" if summary["passed"] else "FAIL"

    print("\nSummary")
    print(f"Total: {summary['total_cases']}")
    print(f"Passed: {summary['passed_cases']}")
    print(f"Failed: {summary['failed_cases']}")
    print(f"Pass rate: {summary['pass_rate']:.1%}")
    print(
        "Required pass rate: "
        f"{summary['required_pass_rate']:.1%}"
    )
    print(f"Overall: {overall}")
    print(f"Report: {output_path}")


## Define command-line arguments.
def _parser():
    parser = argparse.ArgumentParser(
        description=(
            "Run offline fixtures or live "
            "MoodJournal AI evaluations."
        )
    )
    parser.add_argument(
        "--mode",
        choices=["fixtures", "live"],
        default="fixtures",
    )
    parser.add_argument(
        "--deterministic-only",
        action="store_true",
        help="Explicitly confirm that no live model or LLM judge should run.",
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--rubric", type=Path, default=DEFAULT_RUBRIC)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument(
        "--generation-model",
        help="Model used to generate live candidates.",
    )
    parser.add_argument(
        "--judge-model",
        help="Model used to judge live candidates.",
    )
    parser.add_argument("--report", type=Path)
    return parser


## Run the selected evaluation mode.
def main(argv=None):
    parser = _parser()
    args = parser.parse_args(argv)

    dataset = load_json(args.dataset)
    rubric = load_json(args.rubric)

    if args.mode == "fixtures":
        candidates = load_json(args.candidates)
        results = run_cases(dataset, candidates)
        report = make_report(dataset, rubric, results)
        report_prefix = "deterministic"
        passed = report["summary"]["failed_cases"] == 0

    else:
        if args.deterministic_only:
            parser.error(
                "--deterministic-only cannot be used "
                "with --mode live."
            )

        if not args.generation_model:
            parser.error(
                "--generation-model is required "
                "with --mode live."
            )

        if not args.judge_model:
            parser.error(
                "--judge-model is required "
                "with --mode live."
            )

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            parser.error(
                "OPENAI_API_KEY is required "
                "with --mode live."
            )

        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        live_result = run_live_evaluation(
            dataset=dataset,
            rubric=rubric,
            client=client,
            generation_model=args.generation_model,
            judge_model=args.judge_model,
        )

        report = {
            "run_metadata": {
                "mode": "live",
                "deterministic_only": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "dataset_version": live_result["dataset_version"],
                "rubric_version": live_result["rubric_version"],
                "generation_model": live_result["generation_model"],
                "judge_model": live_result["judge_model"],
            },
            "summary": live_result["summary"],
            "cases": live_result["cases"],
        }

        report_prefix = "live"
        passed = report["summary"]["passed"]

    output_path = args.report
    if output_path is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        output_path = REPORTS_DIR / f"{report_prefix}-report-{timestamp}.json"

    output_path = write_report(report, output_path)

    if args.mode == "live":
        print_live_report(report, output_path)
    else:
        print_report(report, output_path)

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
