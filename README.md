# MoodJournal_App


This is a secure full-stack mood journaling application built with React (frontend), Flask (backend), and PostgreSQL (database). Users can register, log in, and manage their mood journals with full CRUD functionality. The backend offers robust APIs with authentication, secure access control, filtering, and analytical features such as word clouds and mood-tag categorization. It also integrates OpenAI to generate weekly mood summaries and personalized self-care suggestions.


## 🔐 Features
- JWT Authentication for secure access.
- User-owned Journal Resource – only the owner can view, create, update, or delete their data.
- Full CRUD operations for journal entries.
- Weekly Analysis – automatically display mood scores and mood tag frequency for each month and week based on real-time dates.
- AI-Powered Insights – uses OpenAI to generate weekly mood summaries and personalized self-care tips.
- Interactive Month Selector – slider to review past months’ analyses within the current year.
- Journal Word Cloud – shows the most frequently used words in monthly journal entries.
- Date-based Filtering – filter journal entries by a custom date range.
- Pagination - supports for large datasets.




## 🧠 Tech Stack
### 🔧 Backend
- Flask: RESTful API Framework
- Flask-SQLAlchemy: ORM for database interaction
- Flask-Migrate: Handles database migrations
- Marshmallow: Schema validation & serialization
- JWT: Authentication
- PostgreSQL/pgAdmin: Database & management
- OpneAI API: AI-powered mood summaries and self-care tips

### 🎨 Frontend
- React: Frontend library
- Axios: For API requests
- React Router: Client-side routing
- Mantine: UI components & styling
- Recharts: Data visualizations for analysis
- Tabler Icons: Icon set for React



## 🛠️ Set Up

  ###  Prerequisite 1: Install PostgreSQL and pgAdmin

  1. Install PostgreSQL
  2. Install pgAdmin
  3. Create a database
     - After installation, create a new database for the app (e.g., moodjournal_db).

```bash
   psql -U postgres
   CREATE DATABASE moodjournal_db;
```

 4. Update database configuration
    - In your Flask app config (or .env file), update the database URI:
```bash
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:<yourpassword>@localhost:5432/tracktrip_db'
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
   git https://github.com/luciayin9944/MoodJournal_App.git
   cd MoodJournal_App
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
