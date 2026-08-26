"""Reset and seed the dedicated Playwright E2E database."""

import os
import sys
from datetime import date, timedelta
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SERVER_DIR = ROOT_DIR / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from app import create_app
from config import db
from models import Journal, JournalEntry, User


TEST_PASSWORD = "password123"


def require_test_database_uri():
    database_uri = os.getenv("E2E_DATABASE_URI") or os.getenv("DATABASE_URI")
    if not database_uri:
        raise RuntimeError("E2E_DATABASE_URI or DATABASE_URI must be set.")
    if "test" not in database_uri.lower():
        raise RuntimeError("Refusing to reset a database whose URI does not contain 'test'.")
    return database_uri


def add_user(username, email):
    user = User(username=username, email=email)
    user.password_hash = TEST_PASSWORD
    db.session.add(user)
    db.session.flush()
    return user


def add_entry(user, entry_date, notes, mood_score=7, mood_tag="Calm"):
    iso_year, iso_week, _ = entry_date.isocalendar()
    journal = Journal.query.filter_by(
        user_id=user.id,
        year=iso_year,
        week_number=iso_week,
    ).first()
    if journal is None:
        journal = Journal(user_id=user.id, year=iso_year, week_number=iso_week)
        db.session.add(journal)
        db.session.flush()

    db.session.add(JournalEntry(
        journal_id=journal.id,
        entry_date=entry_date,
        notes=notes,
        mood_score=mood_score,
        mood_tag=mood_tag,
    ))


def seed_e2e_data():
    today = date.today()
    monday = today - timedelta(days=today.weekday())

    add_user("Login User", "e2e-login@example.com")
    add_user("Create User", "e2e-create@example.com")

    edit_user = add_user("Edit User", "e2e-edit@example.com")
    add_entry(edit_user, today, "Original entry for editing.", 5, "Normal")

    delete_user = add_user("Delete User", "e2e-delete@example.com")
    add_entry(delete_user, today, "Entry that will be deleted.", 6, "Calm")

    history_user = add_user("History User", "e2e-history@example.com")
    add_entry(history_user, monday, "Current week history entry.", 8, "Productive")
    add_entry(
        history_user,
        monday - timedelta(days=7),
        "Previous week history entry.",
        6,
        "Relaxed",
    )

    ai_user = add_user("AI User", "e2e-ai@example.com")
    ai_entries = [
        ("Started the week feeling stressed about work.", 4, "Stressed"),
        ("Made progress and felt more hopeful.", 6, "Hopeful"),
        ("Finished an important task and felt productive.", 8, "Productive"),
        ("Took time to relax and recover.", 7, "Relaxed"),
    ]
    for offset, (notes, score, tag) in enumerate(ai_entries):
        add_entry(ai_user, monday + timedelta(days=offset), notes, score, tag)

    db.session.commit()


if __name__ == "__main__":
    database_uri = require_test_database_uri()
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": database_uri,
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", "e2e-test-secret"),
    })
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_e2e_data()
    print("E2E test database seeded successfully.")
