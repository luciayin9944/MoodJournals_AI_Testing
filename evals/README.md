# Phase 4 LLM Evaluation

Phase 4 is intentionally separate from the deterministic `server/tests` suite.
Live semantic evaluation will be slower, cost-bearing, and probabilistic, so it
must never run as a side effect of normal backend tests.

## Phase 4A assets

- `dataset.json` contains 12 curated evaluation cases covering normal,
  improving, declining, mixed, conflicting, limited-data, extreme,
  hallucination-trap, safety-sensitive, and insufficient-data scenarios.
- `rubric.json` defines five scored dimensions, 1–5 scoring anchors, quality
  thresholds, and a safety hard-fail rule.
- `tests/test_eval_assets.py` validates the dataset and rubric themselves.

`expected_facts` are concise semantic labels for conclusions supported by the
journal evidence. They are not exact strings that a generated summary must copy.
`forbidden_claims` are deliberately unsupported statements used as
hallucination traps. A later LLM judge will compare their meaning with the
candidate response rather than perform exact string matching.

`expected_behavior` is either:

- `generate`: the case contains at least four entries and can enter the AI
  generation pipeline.
- `reject_insufficient_data`: the case has fewer than four entries and should
  be rejected before any provider call.

Run the Phase 4A asset validation from the repository root:

```bash
source server/venv/bin/activate
python -m pytest evals/tests/test_eval_assets.py -v
```

Phase 4A makes no OpenAI API calls and requires no additional dependencies.
The evaluation runner, report generation, live candidate generation, and LLM
judge belong to Phase 4B and Phase 4C and are not implemented yet.
