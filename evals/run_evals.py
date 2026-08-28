"""Command-line runner for Phase 4B offline deterministic evaluations."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from evals.deterministic_checks import check_entries, run_checks


EVALS_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET = EVALS_DIR / "dataset.json"
DEFAULT_RUBRIC = EVALS_DIR / "rubric.json"
DEFAULT_CANDIDATES = EVALS_DIR / "fixtures" / "candidate_responses.json"
REPORTS_DIR = EVALS_DIR / "reports"


def load_json(path):
    with Path(path).open(encoding="utf-8") as source_file:
        return json.load(source_file)


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


def make_summary(results):
    total = len(results)
    passed = sum(result["passed"] for result in results)
    return {
        "total_cases": total,
        "passed_cases": passed,
        "failed_cases": total - passed,
        "pass_rate": passed / total if total else 0.0,
    }


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


def write_report(report, path):
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(report, output_file, indent=2)
        output_file.write("\n")
    return output_path


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


def _parser():
    parser = argparse.ArgumentParser(
        description="Run offline deterministic evaluation cases."
    )
    parser.add_argument("--mode", choices=["fixtures"], default="fixtures")
    parser.add_argument(
        "--deterministic-only",
        action="store_true",
        help="Explicitly confirm that no live model or LLM judge should run.",
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--rubric", type=Path, default=DEFAULT_RUBRIC)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--report", type=Path)
    return parser


def main(argv=None):
    args = _parser().parse_args(argv)
    dataset = load_json(args.dataset)
    rubric = load_json(args.rubric)
    candidates = load_json(args.candidates)
    results = run_cases(dataset, candidates)
    report = make_report(dataset, rubric, results)

    output_path = args.report
    if output_path is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        output_path = REPORTS_DIR / f"deterministic-report-{timestamp}.json"

    output_path = write_report(report, output_path)
    print_report(report, output_path)
    return 0 if report["summary"]["failed_cases"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
