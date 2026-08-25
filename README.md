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
