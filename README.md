# MoodJournals_AI_Testing


## Introduction

MoodJournals AI Testing is a full-stack mood journaling application enhanced with an AI-focused testing framework. The application allows users to record daily moods and journal entries, visualize emotional trends, and receive AI-generated weekly summaries and personalized self-care suggestions powered by the OpenAI API.

This project extends a functional React and Flask application into a practical AI Testing and QA Automation environment. In addition to validating traditional application behavior through UI and API testing, the project focuses on testing AI-powered features whose outputs are non-deterministic and cannot be reliably evaluated using simple expected-value assertions.

The testing framework is designed to cover multiple layers of the system, including:

UI Testing – Automating critical user workflows with Playwright, such as authentication, journal creation, editing, and navigation.

API Testing – Validating Flask REST API endpoints, authentication, request validation, response schemas, and error handling.

AI Output Evaluation – Evaluating AI-generated mood summaries and self-care suggestions for relevance, consistency, safety, and adherence to expected output requirements.

AI Test Generation – Exploring the use of LLMs to generate test scenarios and edge cases from application requirements and API behavior.

Regression Testing – Maintaining repeatable test suites to detect unintended behavior as the application evolves.

Continuous Testing – Integrating automated tests with GitHub Actions so that tests can run automatically as part of the development workflow.

The goal of this project is not only to test whether the application functions correctly, but also to explore the unique challenges of testing LLM-powered software, where quality must be evaluated across both deterministic system behavior and probabilistic AI responses.

## Tech Stack

Application: React, Vite, Mantine, Flask, PostgreSQL, SQLAlchemy, JWT, OpenAI API

Testing: Playwright, Pytest, API Testing, AI/LLM Evaluation

CI/CD: GitHub Actions




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
    - In your Flask app config (or .env file), update the database URI:
```bash
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:<yourpassword>@localhost:5432/moodjournal_testing_db'
```

- Replace <yourpassword> with your actual PostgreSQL password.


 ###  Prerequisite 2: Resgister OpenAI API key

  1. Log in / Sign up at OpenAI. https://auth.openai.com/log-in
  2. Create an API Key: https://platform.openai.com/settings/organization/api-keys
  3. Update your app configuration:
     - In your Flask resources/ai_suggestion.py (or .env file), set the API key:

```bash
    from openai import OpenAI
    import os
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

   - Replace OPENAI_API_KEY in your environment variables with your actual API key.
  



 ### Clone the repository

```bash
   git https://github.com/luciayin9944/MoodJournals_AI_Testing.git
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

    flask db init
    flask db migrate -m "initial migration"
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

## Phase 1 API Tests

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

## Phase 2 Playwright E2E Tests

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

## Phase 3 Deterministic AI Tests

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

## Phase 4 AI Evaluation Framework

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
