"""Embedding storage contracts; semantic retrieval needs PostgreSQL tests."""

from pathlib import Path

import pytest
from flask_migrate import Migrate, downgrade, upgrade
from sqlalchemy import inspect, text
from sqlalchemy.exc import StatementError

from app import create_app
from config import db
from models import JournalEntry


def test_null_embedding(client, auth_headers, valid_entry_payload):
    response = client.post('/entries', json=valid_entry_payload, headers=auth_headers)

    assert response.status_code == 201
    result = response.get_json()
    assert 'embedding' not in result
    assert db.session.get(JournalEntry, result['id']).embedding is None


def test_embedding_round_trip(
    client, auth_headers, make_entry, user_a
):
    entry = make_entry(user_a)
    entry_id = entry.id
    embedding = [0.125, -0.25, 0.5] * 512
    entry.embedding = embedding
    db.session.commit()
    db.session.remove()

    stored = db.session.get(JournalEntry, entry_id)
    assert list(stored.embedding) == pytest.approx(embedding)
    response = client.get(f'/entries/{entry_id}', headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()['notes'] == stored.notes
    assert 'embedding' not in response.get_json()


def test_invalid_embedding_dimension(make_entry, user_a):
    entry = make_entry(user_a, notes='Original journal content.')
    entry_id = entry.id
    entry.embedding = [0.1, 0.2, 0.3]
    entry.notes = 'This update must be rolled back.'

    with pytest.raises(StatementError, match='expected 1536 dimensions'):
        db.session.commit()
    db.session.rollback()
    db.session.remove()

    stored = db.session.get(JournalEntry, entry_id)
    assert stored.embedding is None
    assert stored.notes == 'Original journal content.'


def test_migration_round_trip(tmp_path):
    # Always use a fresh temporary database, never DATABASE_URI/TEST_DATABASE_URI.
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{tmp_path / "migration.db"}',
    })
    Migrate(app, db)
    directory = str(Path(__file__).resolve().parents[1] / 'migrations')
    original_revision = '7596ddc82698'

    with app.app_context():
        upgrade(directory=directory, revision=original_revision)
        with db.engine.begin() as conn:
            conn.execute(text("INSERT INTO users (id, username, email) VALUES (1, 'fixture', 'fixture@example.com')"))
            conn.execute(text('INSERT INTO journals (id, year, week_number, user_id) VALUES (1, 2026, 1, 1)'))
            conn.execute(text("INSERT INTO journal_entries (id, entry_date, notes, mood_score, mood_tag, journal_id) VALUES (1, '2026-01-01', 'Existing journal evidence.', 7, 'Calm', 1)"))
            conn.execute(text("INSERT INTO suggestions (id, summary, selfcare_tips, journal_id) VALUES (1, 'Existing summary.', '[]', 1)"))

        def snapshot():
            with db.engine.connect() as conn:
                return {
                    table: conn.execute(text(query)).fetchall()
                    for table, query in {
                        'users': 'SELECT * FROM users ORDER BY id',
                        'journals': 'SELECT * FROM journals ORDER BY id',
                        'journal_entries': 'SELECT id, entry_date, notes, mood_score, mood_tag, journal_id FROM journal_entries ORDER BY id',
                        'suggestions': 'SELECT * FROM suggestions ORDER BY id',
                    }.items()
                }

        before = snapshot()
        upgrade(directory=directory)
        upgrade(directory=directory)  # An already-applied revision is a no-op.
        assert snapshot() == before
        column = next(c for c in inspect(db.engine).get_columns('journal_entries') if c['name'] == 'embedding')
        assert column['nullable'] is True
        with db.engine.connect() as conn:
            assert conn.execute(text('SELECT embedding FROM journal_entries')).scalar_one() is None
            assert conn.execute(text('SELECT version_num FROM alembic_version')).scalar_one() == 'b70c1a4d9e26'

        downgrade(directory=directory, revision=original_revision)
        assert snapshot() == before
        assert 'embedding' not in {c['name'] for c in inspect(db.engine).get_columns('journal_entries')}
