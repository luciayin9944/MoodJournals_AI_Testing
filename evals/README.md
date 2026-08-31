# Phase 4 AI Evaluation Framework

Phase 4 evaluates the quality of AI-generated weekly mood summaries and
self-care suggestions. It is intentionally separate from the deterministic
`server/tests` suite because live semantic evaluation is slower, cost-bearing,
and probabilistic. Live evaluation never runs as a side effect of normal
backend or evaluation unit tests.

## Architecture

- `dataset.json` contains 12 curated cases covering normal, improving,
  declining, mixed, conflicting, limited-data, extreme, hallucination-trap,
  safety-sensitive, and insufficient-data scenarios.
- `rubric.json` defines groundedness, relevance, hallucination control, safety,
  and tone, along with 1–5 scoring anchors, per-dimension thresholds, a minimum
  average score, and a minimum dataset pass rate.
- `fixtures/candidate_responses.json` provides fixed candidates for repeatable
  offline evaluation.
- `deterministic_checks.py` applies the Phase 3 contract, safety-pattern, and
  basic date/number-groundedness validators.
- `generation.py` requests a structured candidate from a live generation model
  and validates it before evaluation continues.
- `judge.py` requests structured semantic scores from an LLM judge and applies
  the deterministic rubric thresholds.
- `live_eval.py` coordinates generation, deterministic checks, judging, and
  case-level and dataset-level pass decisions.
- `run_evals.py` exposes safe `fixtures` and explicit `live` command-line modes
  and writes machine-readable JSON reports.

## Dataset labels

`expected_facts` describe conclusions supported by the journal evidence. They
are semantic reference labels, not exact strings the candidate must copy.

`forbidden_claims` are deliberately unsupported statements used as
hallucination traps. The LLM judge compares their meaning with the candidate
instead of relying on exact string matching.

`expected_behavior` is either:

- `generate`: at least four entries are available and the case may enter the AI
  generation pipeline.
- `reject_insufficient_data`: fewer than four entries are available, so the
  case must stop before any provider request.

## Run the unit tests

From the repository root:

```bash
source server/venv/bin/activate
python -m pytest evals/tests -v
```

The unit tests use fixtures, monkeypatching, and fake clients. They do not call
the real OpenAI API and do not require an API key.

Run an individual area when diagnosing a failure:

```bash
python -m pytest evals/tests/test_eval_assets.py -v
python -m pytest evals/tests/test_checks.py -v
python -m pytest evals/tests/test_generation.py -v
python -m pytest evals/tests/test_judge.py -v
python -m pytest evals/tests/test_live_eval.py -v
python -m pytest evals/tests/test_runner.py -v
```

## Offline fixture evaluation

Offline mode reads `fixtures/candidate_responses.json`, runs deterministic
checks, and never creates an OpenAI client:

```bash
python -m evals.run_evals --mode fixtures --deterministic-only
```

Fixtures are the default, so this shorter command is also offline:

```bash
python -m evals.run_evals
```

Offline mode exits with code `0` only when every deterministic case passes. It
exits with code `1` when any case fails.

## Live generation and LLM judge

Copy the committed template to the ignored local environment file if needed:

```bash
cp .env.evals.example .env.evals
```

Add the real key only to `.env.evals`, then export its values into the current
terminal session:

```bash
set -a
source .env.evals
set +a
```

Run live evaluation with explicit generation and judge models:

```bash
python -m evals.run_evals \
  --mode live \
  --generation-model YOUR_GENERATION_MODEL \
  --judge-model YOUR_JUDGE_MODEL
```

For each `generate` case, live mode normally makes one generation request and
one judge request. Insufficient-data cases are rejected before any model call.
Live mode therefore requires network access, a valid API key, model access, and
incurs API usage costs.

The LLM produces semantic scores, but Python applies the fixed thresholds from
`rubric.json`. A live run exits with code `0` when the dataset pass rate reaches
`minimum_case_pass_rate`; otherwise it exits with code `1`. Invalid command-line
configuration exits with code `2`.

## Live smoke test

`fixtures/live_smoke_dataset.json` contains one tracked example case for a
lower-cost live integration check. It verifies the generation request,
structured response validation, deterministic checks, LLM judge, rubric
application, and report writing without running the full 12-case dataset.

The smoke case is example test data, not a generated response or production user
data. Replace the case locally, or pass another JSON file with `--dataset`, when
testing a different scenario. Keep the same dataset fields so generation and the
judge receive the required evidence and labels.

After loading `.env.evals`, run:

```bash
python -m evals.run_evals \
  --mode live \
  --dataset evals/fixtures/live_smoke_dataset.json \
  --generation-model gpt-4o-mini \
  --judge-model gpt-4o-mini \
  --report evals/reports/live-smoke-report.json
```

This single `generate` case normally makes one generation request and one judge
request. Replace the model IDs if they are unavailable to your API project. An
exit code of `0` means the case completed and passed the rubric. An exit code of
`1` can mean the live pipeline completed but the candidate did not meet the
quality thresholds; inspect the report to distinguish evaluation failure from a
provider or pipeline error.

## Reports and secrets

Generated reports are written to `evals/reports/`:

```text
deterministic-report-YYYYMMDD-HHMMSS.json
live-report-YYYYMMDD-HHMMSS.json
```

Generated report JSON files are ignored by Git. `.env.evals` is also ignored
and must never be committed. `.env.evals.example` contains only a safe empty
placeholder and may be committed.
