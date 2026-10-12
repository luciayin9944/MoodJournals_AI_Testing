# MoodJournals


## Introduction

MoodJournals is a full-stack mood journaling app for recording daily experiences and exploring emotional patterns over time. Users can track mood scores and tags, view monthly charts and word clouds, and generate weekly summaries with self-care suggestions.

The **Long-Term Insights** page uses retrieval-augmented generation (RAG) to answer questions about your journal history. Choose a question and a time range to explore topics such as stress, sleep, work, and activities that improve your mood. Each analysis includes an answer, any identified patterns, and the journal entries used as evidence.

Long-Term Insights uses selected relevant entries, rather than every entry in your history. Weekly Insights uses the entries from one specific week.

### How RAG Works

1. Each journal entry's mood tag, score, and notes are converted into an embedding and stored in PostgreSQL. New and edited entries attempt this automatically; seeded entries need the backfill script.
2. Your selected question is converted into an embedding. Retrieval searches your entries within the selected date range and chooses the closest matches using cosine distance.
3. The generation model receives the question and retrieved entries to produce an answer and patterns. The backend adds those entries as sources so you can review the evidence.


## Tech Stack

- **Frontend:** React, Vite, Mantine, Axios, React Router, Recharts, and Day.js.
- **Backend:** Python, Flask, SQLAlchemy, Flask-Migrate, and JWT authentication.
- **Database:** PostgreSQL with pgvector for storing and searching journal embeddings.
- **AI:** OpenAI API; `text-embedding-3-small` for embeddings and `gpt-4o-mini` as the default generation model.



## 🛠️ Set Up

  ###  Prerequisite 1: Install PostgreSQL and pgAdmin

  1. Install PostgreSQL
  2. Install pgAdmin
  3. Create a database
     - After installation, create a new database for the app (e.g., moodjournal_db).

```bash
psql -U postgres
```

In the PostgreSQL prompt:

```sql
CREATE DATABASE moodjournal_testing_db;
```

Enter `\q` to exit PostgreSQL and return to your terminal.


 ###  Prerequisite 2: Register an OpenAI API key

  1. Log in / Sign up at OpenAI. https://auth.openai.com/log-in
  2. Create an API Key: https://platform.openai.com/settings/organization/api-keys
  3. Save the key for the configuration step below.

 ###  Prerequisite 3: Install PostgreSQL’s pgvector extension

These commands are for **macOS with Homebrew PostgreSQL 14**.

 1. Run in a terminal, outside the project directory.

```bash
export PG_CONFIG="$(brew --prefix postgresql@14)/bin/pg_config"
```

 2. Download and install pgvector.

```bash
(
    cd "$(mktemp -d)" &&
    git clone --branch v0.8.7 https://github.com/pgvector/pgvector.git &&
    cd pgvector &&
    make &&
    make install
)
```


 ### Clone the repository

```bash
   git clone https://github.com/luciayin9944/MoodJournals_AI_Testing.git
   cd MoodJournals_AI_Testing
```

 ### Set up configuration

Create `server/.env` with your database settings and API key:

```dotenv
DATABASE_URI=postgresql://postgres:<yourpassword>@localhost:5432/moodjournal_testing_db
JWT_SECRET_KEY=<your-local-secret>
OPENAI_API_KEY=<your-openai-api-key>
```

- Replace the placeholders with your own values. Never commit `server/.env`.



### Start the Backend

Run `seed.py` only against a disposable local database; it replaces existing app data with demo data.

```bash
    cd server
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

    export FLASK_APP=run.py
    export FLASK_ENV=development

    flask db upgrade head
    python seed.py
    python ../scripts/backfill_embeddings.py

```

Run the Flask server:

```bash
    python run.py
```

### Start the Frontend
In another terminal, from the repository root:

```bash
    cd client
    npm install
    npm run dev
```

- Open the URL printed by Vite, usually **http://localhost:5173**. 
- For seeded demo data, sign in with **`test@example.com` / `password123`**.

## 🛠️ Evaluation

Run the following commands from the **repository root**.

### Retrieval Evaluation
```bash
    PYTHONPATH=server server/venv/bin/python evals/rag/evaluate_retrieval.py
```

### Embedding Model Comparison
Compare: text-embedding-3-small vs text-embedding-3-large
```bash
    PYTHONPATH=server server/venv/bin/python evals/rag/compare_embedding_models.py
```


### Generation Evaluation
```bash
    PYTHONPATH=server server/venv/bin/python -m evals.rag.evaluate_rag_generation
```
