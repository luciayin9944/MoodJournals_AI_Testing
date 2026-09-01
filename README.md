# MoodJournals_AI_Testing


## Introduction

MoodJournals AI Testing is a full-stack mood journaling application enhanced with an AI-focused testing framework. The application allows users to record daily moods and journal entries, visualize emotional trends, and receive AI-generated weekly summaries and personalized self-care suggestions powered by the OpenAI API.

This project extends a functional React and Flask application into a practical AI Testing and QA Automation environment. In addition to validating traditional application behavior through UI and API testing, the project focuses on testing AI-powered features whose outputs are non-deterministic and cannot be reliably evaluated using simple expected-value assertions.

The testing framework is designed to cover multiple layers of the system, including:

- UI Testing – Automating critical user workflows with Playwright, such as authentication, journal creation, editing, and navigation.

- API Testing – Validating Flask REST API endpoints, authentication, request validation, response schemas, and error handling.

- AI Output Evaluation – Evaluating AI-generated mood summaries and self-care suggestions for relevance, consistency, safety, and adherence to expected output requirements.

- AI Test Design – Building curated datasets, edge cases, hallucination traps, and scoring rubrics for repeatable AI quality evaluation.

- Regression Testing – Re-running the backend API, deterministic AI, offline evaluation, and Playwright E2E suites to detect regressions whenever the application changes.

- Continuous Testing – Automatically running deterministic regression suites on pushes and pull requests with GitHub Actions, while keeping cost-bearing live AI evaluations manually triggered.

The goal of this project is not only to test whether the application functions correctly, but also to explore the unique challenges of testing LLM-powered software, where quality must be evaluated across both deterministic system behavior and probabilistic AI responses.

## Tech Stack

- Application: React, Vite, Mantine, Flask, PostgreSQL, SQLAlchemy, JWT, OpenAI API

- Testing: Playwright, pytest, API Testing, AI/LLM Evaluation

- Continuous Integration: GitHub Actions




## 🛠️ Set Up

  ###  Prerequisite 1: Install PostgreSQL and pgAdmin

  1. Install PostgreSQL
  2. Install pgAdmin
  3. Create a database
     - After installation, create a new database for the app (e.g., moodjournal_db).

```bash
   psql -U postgres
   CREATE DATABASE moodjournal_testing_db;
```

 4. Update database configuration
    - In `server/.env`, set the database URI:

```text
DATABASE_URI=postgresql://postgres:<yourpassword>@localhost:5432/moodjournal_testing_db
JWT_SECRET_KEY=<your-local-secret>
```

- Replace `<yourpassword>` and `<your-local-secret>` with local values. Never commit `server/.env`.


 ###  Prerequisite 2: Register an OpenAI API key

  1. Log in / Sign up at OpenAI. https://auth.openai.com/log-in
  2. Create an API Key: https://platform.openai.com/settings/organization/api-keys
  3. Add the key to `server/.env` only when running the application with live AI features:

```text
OPENAI_API_KEY=<your-openai-api-key>
```

- Deterministic API, AI, offline evaluation, and Playwright tests do not require this key.
  



 ### Clone the repository

```bash
   git clone https://github.com/luciayin9944/MoodJournals_AI_Testing.git
   cd MoodJournals_AI_Testing
```


### Set Up the Backend

```bash
    cd server
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

    export FLASK_APP=run.py
    export FLASK_ENV=development

    flask db upgrade head
    python seed.py
```

Run the Flask server:

```bash
    python run.py
```

### Start the Frontend
In another terminal, from the client directory:

```bash
    cd client
    npm install
    npm run dev
```


## Phases

### Phase 1 API Tests

Install the application and test dependencies in the backend virtual environment:

```bash
pip install -r server/requirements.txt
pip install -r server/requirements-test.txt
```

Run the isolated API suite from the repository root:

```bash
pytest server/tests
```

Tests use an in-memory database by default and never call the real OpenAI API. To run
against PostgreSQL, copy `.env.test.example` to `.env.test`, use a dedicated test
database, export the variables from that file, and then run the same command:

```bash
set -a
source .env.test
set +a
pytest server/tests
```

Never set `TEST_DATABASE_URI` to a development or production database because the
test fixture creates and drops its schema for every test.

### Phase 2 Playwright E2E Tests

Install the frontend dependencies and the Chromium test browser once:

```bash
cd client
npm install
npx playwright install chromium
```

Run all seven E2E flows from the `client` directory:

```bash
npm run test:e2e
```

Playwright automatically resets deterministic test data, starts Flask and Vite,
runs the Chromium tests with one worker, and stops both servers. By default it
uses the isolated `/tmp/moodjournal_e2e_test.db` SQLite database. To use a dedicated
PostgreSQL test database instead, set a URI whose database name contains `test`:

```bash
E2E_DATABASE_URI=postgresql://postgres:password@localhost:5432/moodjournal_e2e_test npm run test:e2e
```

Never point `E2E_DATABASE_URI` at development or production data. The E2E seed
script intentionally drops and recreates all tables, and refuses database URIs
that do not contain the word `test`.

Useful Playwright commands:

```bash
npm run test:e2e:headed
npm run test:e2e:ui
npx playwright test tests/auth.spec.js
npx playwright show-report
```

The AI suggestion browser flow uses a deterministic mocked response and never
calls the real OpenAI API.

### Phase 3 Deterministic AI Tests

Phase 3 validates the AI response contract, deterministic safety rules, and
basic groundedness before an AI result can be stored or evaluated further.

The contract tests cover JSON parsing, standard JSON code fences, required
fields, field types, non-empty values, exactly three self-care tips,
normalization, and database-aligned length limits. Safety checks use narrow,
explainable rules to reject direct diagnoses, unsafe medication instructions,
discouragement of professional support, and encouragement of self-harm. Basic
groundedness verifies that concrete dates and numbers in a summary also appear
in the source journal entries.

Run all deterministic AI tests from the repository root:

```bash
source server/venv/bin/activate
python -m pytest server/tests/ai -v
```

Run only contract or safety and groundedness tests:

```bash
python -m pytest server/tests/ai/test_ai_contract.py -v
python -m pytest server/tests/ai/test_ai_safety.py -v
```

Run the complete backend regression suite:

```bash
python -m pytest server/tests -v
```

Phase 3 uses fixed local fixtures and mocked provider responses. It requires no
OpenAI API key or network access.

### Phase 4 AI Evaluation Framework

Phase 4 evaluates qualities that deterministic assertions cannot fully measure,
including semantic relevance, paraphrase-level groundedness, hallucination
control, nuanced safety, and supportive tone.

The framework includes:

- A curated 12-case evaluation dataset with expected facts and forbidden claims.
- A five-dimension, 1–5 scoring rubric with deterministic quality thresholds.
- An offline fixture runner for repeatable contract, safety, and basic
  groundedness regression checks.
- Live candidate generation followed by an LLM-as-a-judge evaluation.
- Case-level and dataset-level pass decisions with machine-readable JSON reports.

Run all evaluation unit tests without calling OpenAI:

```bash
source server/venv/bin/activate
python -m pytest evals/tests -v
```

Run the offline fixture evaluation:

```bash
python -m evals.run_evals --mode fixtures --deterministic-only
```

To run live evaluation, copy the safe template, add the real API key only to the
ignored `.env.evals` file, and load it into the current terminal:

```bash
cp .env.evals.example .env.evals
set -a
source .env.evals
set +a
```

Then explicitly select the generation and judge models:

```bash
python -m evals.run_evals \
  --mode live \
  --generation-model YOUR_GENERATION_MODEL \
  --judge-model YOUR_JUDGE_MODEL
```

Live mode calls the real OpenAI API, requires network and model access, and
incurs API usage costs. Generated reports are saved under `evals/reports/` and
ignored by Git. See `evals/README.md` for the architecture, evaluation logic,
commands, exit-code behavior, and secret-handling details.

For a lower-cost live integration check, run the tracked single-case smoke
dataset after loading `.env.evals`:

```bash
python -m evals.run_evals \
  --mode live \
  --dataset evals/fixtures/live_smoke_dataset.json \
  --generation-model gpt-4o-mini \
  --judge-model gpt-4o-mini \
  --report evals/reports/live-smoke-report.json
```

The smoke dataset is example test data and may be replaced locally when testing
a different scenario. This command calls the real OpenAI API and normally makes
one generation request and one judge request.

### Phase 5 GitHub Actions Continuous Testing

Phase 5 runs the existing test layers in GitHub Actions. It separates fast,
deterministic checks from live, cost-bearing AI evaluation so that normal code
changes can be validated automatically without exposing an API key or calling
OpenAI.

#### Deterministic CI

The `.github/workflows/ci.yml` workflow runs automatically when code is pushed
to `main` or when a pull request targets `main`. It can also be started manually
from the GitHub Actions page.

The workflow runs three jobs in parallel:

- Backend API tests, Phase 3 deterministic AI tests, Phase 4 evaluation unit
  tests, and the 12-case offline fixture evaluation.
- Frontend lint and production build.
- All seven Playwright Chromium E2E tests.

The API tests use an isolated in-memory SQLite database. Playwright resets a
dedicated SQLite E2E database and uses a mocked AI suggestion response. This
workflow requires no `OPENAI_API_KEY`, makes no live OpenAI requests, and incurs
no OpenAI API cost.

Test reports, the frontend build, and Playwright failure evidence are uploaded
as GitHub Actions artifacts. The deterministic jobs are suitable for required
pull-request checks because a failure represents a repeatable application or
test regression.

#### Manual live AI smoke evaluation

The `.github/workflows/live-ai-eval.yml` workflow is intentionally limited to
manual `workflow_dispatch` runs. It evaluates the tracked one-case smoke dataset
through the complete live pipeline:

1. Generate a candidate response with OpenAI.
2. Apply deterministic contract, safety, and groundedness checks.
3. Score the candidate with an LLM-as-a-judge.
4. Apply the fixed Phase 4 rubric thresholds.
5. Upload the machine-readable JSON report as a GitHub Actions artifact.

Before running it, add an Actions repository secret named `OPENAI_API_KEY`:

```text
Repository Settings
→ Secrets and variables
→ Actions
→ New repository secret
→ OPENAI_API_KEY
```

Run it from:

```text
GitHub repository
→ Actions
→ Live AI Evaluation
→ Run workflow
```

The form allows the generation and judge model IDs to be selected. The default
smoke run normally makes one generation request and one judge request, so it
requires network and model access and incurs OpenAI API cost. Because it is
manual, probabilistic, and cost-bearing, it does not run on every push or pull
request and should not be configured as a required merge check.

This phase implements continuous testing rather than application deployment. A
deployment workflow can be added later after a hosting platform, production
environment, database migration strategy, and rollback process are defined.
