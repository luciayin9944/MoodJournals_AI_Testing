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


## Testing Setup

Run the following commands from the repository root unless a different directory is specified.

### Install Test Dependencies

Create the backend virtual environment and install the application and test dependencies:

```bash
python3 -m venv server/venv
server/venv/bin/python -m pip install --upgrade pip
server/venv/bin/python -m pip install -r server/requirements.txt
server/venv/bin/python -m pip install -r server/requirements-test.txt
```

Install the frontend dependencies and Chromium:

```bash
cd client
npm ci
npx playwright install chromium
cd ..
```

### Run Deterministic Tests

Run the backend API and deterministic AI tests:

```bash
server/venv/bin/python -m pytest server/tests -v
```

Run the AI evaluation unit tests:

```bash
server/venv/bin/python -m pytest evals/tests -v
```

Run the offline fixture evaluation:

```bash
server/venv/bin/python -m evals.run_evals \
  --mode fixtures \
  --deterministic-only
```

Run the frontend lint and production build:

```bash
cd client
npm run lint
npm run build
cd ..
```

Run the Playwright E2E tests:

```bash
cd client
npm run test:e2e
cd ..
```

The deterministic test suites use isolated test data and mocked or fixture-based AI responses. They do not require `OPENAI_API_KEY` and do not call the live OpenAI API.

By default:

- Pytest uses an in-memory SQLite database.
- Playwright uses `/tmp/moodjournal_e2e_test.db`.
- The Playwright AI suggestion flow uses a mocked response.

To run pytest against PostgreSQL, copy the test environment template and configure a dedicated test database:

```bash
cp .env.test.example .env.test
```

Update `TEST_DATABASE_URI` in `.env.test`, then load the environment and run the tests:

```bash
set -a
source .env.test
set +a

server/venv/bin/python -m pytest server/tests -v
```


### Run the Optional Live AI Smoke Evaluation

Copy the live evaluation environment template:

```bash
cp .env.evals.example .env.evals
```

Add a real OpenAI API key to the ignored `.env.evals` file:

```text
OPENAI_API_KEY=<your-openai-api-key>
```

Load the environment variables:

```bash
set -a
source .env.evals
set +a
```

Run the single-case live smoke evaluation:

```bash
server/venv/bin/python -m evals.run_evals \
  --mode live \
  --dataset evals/fixtures/live_smoke_dataset.json \
  --generation-model gpt-4o-mini \
  --judge-model gpt-4o-mini \
  --report evals/reports/live-smoke-report.json
```

Live evaluation requires:

- Network access
- A valid `OPENAI_API_KEY`
- Access to the selected models
- OpenAI API usage costs

Generated reports are saved under `evals/reports/` and are ignored by Git.

### GitHub Actions

The deterministic CI workflow is defined in:

```text
.github/workflows/ci.yml
```

It runs automatically when:

- Code is pushed to `main`.
- A pull request targets `main`.
- It is manually started from GitHub Actions.

It runs:

- Backend API and deterministic AI tests
- AI evaluation unit tests
- Offline fixture evaluation
- Frontend lint and production build
- Playwright Chromium E2E tests

The deterministic workflow does not require `OPENAI_API_KEY` and does not incur OpenAI API costs.

The live AI smoke workflow is defined in:

```text
.github/workflows/live-ai-eval.yml
```

Before running it, add `OPENAI_API_KEY` under:

```text
Repository Settings
→ Secrets and variables
→ Actions
→ New repository secret
```

Run the workflow from:

```text
GitHub repository
→ Actions
→ Live AI Evaluation
→ Run workflow
```

The live AI workflow is manually triggered because it calls the real OpenAI API, incurs usage costs, and may produce probabilistic results.



