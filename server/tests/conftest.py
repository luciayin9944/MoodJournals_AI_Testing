import os
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest


SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from app import create_app
from config import db
from models import Journal, JournalEntry, User


@pytest.fixture()
def app():
    test_database_uri = os.getenv("TEST_DATABASE_URI", "sqlite:///:memory:")
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": test_database_uri,
        "JWT_SECRET_KEY": "phase-1-test-secret",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def make_user(app):
    created = []

    def _make_user(username, email, password="password123"):
        user = User(username=username, email=email)
        user.password_hash = password
        db.session.add(user)
        db.session.commit()
        created.append(user)
        return user

    return _make_user


@pytest.fixture()
def user_a(make_user):
    return make_user("user_a", "user-a@example.com")


@pytest.fixture()
def user_b(make_user):
    return make_user("user_b", "user-b@example.com")


def _login_headers(client, email, password="password123"):
    response = client.post("/login", json={"email": email, "password": password})
    token = response.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def auth_headers(client, user_a):
    return _login_headers(client, user_a.email)


@pytest.fixture()
def other_user_headers(client, user_b):
    return _login_headers(client, user_b.email)


@pytest.fixture()
def make_entry(app):
    def _make_entry(
        user,
        entry_date=None,
        mood_score=7,
        mood_tag="Calm",
        notes="A deterministic journal entry.",
    ):
        entry_date = entry_date or date.today()
        iso_year, iso_week, _ = entry_date.isocalendar()
        journal = Journal.query.filter_by(
            user_id=user.id,
            year=iso_year,
            week_number=iso_week,
        ).first()
        if journal is None:
            journal = Journal(user_id=user.id, year=iso_year, week_number=iso_week)
            db.session.add(journal)

        entry = JournalEntry(
            journal=journal,
            entry_date=entry_date,
            mood_score=mood_score,
            mood_tag=mood_tag,
            notes=notes,
        )
        db.session.add(entry)
        db.session.commit()
        return entry

    return _make_entry


@pytest.fixture()
def current_week_dates():
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return [monday + timedelta(days=offset) for offset in range(7)]


@pytest.fixture()
def valid_entry_payload():
    return {
        "entry_date": date.today().isoformat(),
        "notes": "I had a calm and productive day.",
        "mood_score": 7,
        "mood_tag": "Calm",
    }
