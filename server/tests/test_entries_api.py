from datetime import date, timedelta
from unittest.mock import Mock

import pytest

from config import db
from models import Journal, JournalEntry
from services import embedding_service
from services.exceptions import ProviderTimeoutError


def test_create_entry_returns_created_entry(client, auth_headers, valid_entry_payload):
    response = client.post("/entries", json=valid_entry_payload, headers=auth_headers)

    assert response.status_code == 201
    body = response.get_json()
    assert body["entry_date"] == valid_entry_payload["entry_date"]
    assert body["mood_score"] == 7
    assert body["mood_tag"] == "Calm"


def test_create_entry_creates_iso_week_journal(
    client, auth_headers, user_a, valid_entry_payload
):
    response = client.post("/entries", json=valid_entry_payload, headers=auth_headers)

    assert response.status_code == 201
    iso_year, iso_week, _ = date.fromisoformat(valid_entry_payload["entry_date"]).isocalendar()
    journal = Journal.query.filter_by(
        user_id=user_a.id,
        year=iso_year,
        week_number=iso_week,
    ).one()
    assert journal.journal_entries[0].id == response.get_json()["id"]


@pytest.mark.parametrize("entry_date", [None, "not-a-date"])
def test_create_entry_rejects_invalid_date(
    client, auth_headers, valid_entry_payload, entry_date
):
    valid_entry_payload["entry_date"] = entry_date

    response = client.post("/entries", json=valid_entry_payload, headers=auth_headers)

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid date format. Use YYYY-MM-DD"


@pytest.mark.parametrize("mood_score", [0, 11])
def test_create_entry_rejects_out_of_range_mood_score(
    client, auth_headers, valid_entry_payload, mood_score
):
    valid_entry_payload["mood_score"] = mood_score

    response = client.post("/entries", json=valid_entry_payload, headers=auth_headers)

    assert response.status_code == 400
    assert "Mood score must be between 1 and 10" in response.get_json()["errors"][0]
    assert JournalEntry.query.count() == 0


def test_create_entry_rejects_invalid_mood_tag(
    client, auth_headers, valid_entry_payload
):
    valid_entry_payload["mood_tag"] = "Confused-but-not-allowed"

    response = client.post("/entries", json=valid_entry_payload, headers=auth_headers)

    assert response.status_code == 400
    assert "Invalid mood tag" in response.get_json()["errors"][0]


def test_create_entry_rejects_duplicate_date(
    client, auth_headers, make_entry, user_a, valid_entry_payload
):
    make_entry(user_a, date.fromisoformat(valid_entry_payload["entry_date"]))

    response = client.post("/entries", json=valid_entry_payload, headers=auth_headers)

    assert response.status_code == 400
    assert response.get_json()["error"] == "Entry for this date already exists."


def test_edit_own_entry(client, auth_headers, make_entry, user_a):
    entry = make_entry(user_a)

    response = client.patch(
        f"/entries/{entry.id}",
        json={"mood_score": 9, "mood_tag": "Joyful", "notes": "Updated notes."},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.get_json()["mood_score"] == 9
    assert response.get_json()["notes"] == "Updated notes."


def test_delete_own_entry(client, auth_headers, make_entry, user_a):
    entry = make_entry(user_a)
    entry_id = entry.id

    response = client.delete(f"/entries/{entry_id}", headers=auth_headers)

    assert response.status_code == 200
    assert db.session.get(JournalEntry, entry_id) is None


@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_user_cannot_access_another_users_entry(
    client, auth_headers, make_entry, user_b, method
):
    entry = make_entry(user_b)
    request_method = getattr(client, method)
    kwargs = {"headers": auth_headers}
    if method == "patch":
        kwargs["json"] = {"notes": "Unauthorized change."}

    response = request_method(f"/entries/{entry.id}", **kwargs)

    assert response.status_code == 404


@pytest.fixture()
def embedded_entry(make_entry, user_a):
    entry = make_entry(user_a)
    entry.embedding = [0.25] * 1536
    db.session.commit()
    return entry


@pytest.fixture()
def embedder(monkeypatch):
    mock = Mock(return_value=[0.5] * 1536)
    monkeypatch.setattr(embedding_service, "generate_entry_embedding", mock)
    return mock


@pytest.mark.parametrize("field,value", [
    ("notes", "A better day."),
    ("mood_score", 9),
    ("mood_tag", "Joyful"),
])
def test_patch_embedding(client, auth_headers, embedded_entry, embedder, field, value):
    entry_id = embedded_entry.id

    response = client.patch(
        f"/entries/{entry_id}", json={field: value}, headers=auth_headers,
    )

    assert response.status_code == 200
    embedder.assert_called_once_with(embedded_entry)
    db.session.remove()
    stored = db.session.get(JournalEntry, entry_id)
    assert getattr(stored, field) == value
    assert list(stored.embedding) == pytest.approx([0.5] * 1536)


@pytest.mark.parametrize("change", ["same", "date", "empty"])
def test_patch_keeps_embedding(
    client, auth_headers, embedded_entry, embedder, change
):
    entry_id = embedded_entry.id
    if change == "same":
        data = {field: getattr(embedded_entry, field)
                for field in ("notes", "mood_score", "mood_tag")}
    elif change == "date":
        data = {"entry_date": (embedded_entry.entry_date + timedelta(days=1)).isoformat()}
    else:
        data = {}

    response = client.patch(f"/entries/{entry_id}", json=data, headers=auth_headers)

    assert response.status_code == 200
    embedder.assert_not_called()
    db.session.remove()
    assert list(db.session.get(JournalEntry, entry_id).embedding) == pytest.approx([0.25] * 1536)


@pytest.mark.parametrize("failure", ["provider", "storage"])
def test_patch_embedding_failure(
    client, auth_headers, embedded_entry, embedder, failure
):
    entry_id = embedded_entry.id
    if failure == "provider":
        embedder.side_effect = ProviderTimeoutError("Timed out")
    else:
        # A wrong-sized vector causes the second database commit to fail.
        embedder.return_value = [0.5]

    response = client.patch(
        f"/entries/{entry_id}", json={"notes": "Saved despite embedding failure."},
        headers=auth_headers,
    )

    assert response.status_code == 200
    embedder.assert_called_once()
    db.session.remove()
    stored = db.session.get(JournalEntry, entry_id)
    assert stored.notes == "Saved despite embedding failure."
    assert stored.embedding is None


def test_patch_invalid(client, auth_headers, embedded_entry, embedder):
    entry_id = embedded_entry.id
    old_notes = embedded_entry.notes

    response = client.patch(
        f"/entries/{entry_id}",
        json={"notes": "Should roll back.", "mood_score": 11},
        headers=auth_headers,
    )

    assert response.status_code == 400
    embedder.assert_not_called()
    db.session.remove()
    stored = db.session.get(JournalEntry, entry_id)
    assert stored.notes == old_notes
    assert list(stored.embedding) == pytest.approx([0.25] * 1536)


@pytest.mark.parametrize("change", ["null", "different"])
def test_patch_ignores_date(
    client, auth_headers, embedded_entry, embedder, change
):
    entry_id = embedded_entry.id
    old_date = embedded_entry.entry_date
    new_date = None if change == "null" else (old_date + timedelta(days=1)).isoformat()

    response = client.patch(
        f"/entries/{entry_id}", json={"entry_date": new_date}, headers=auth_headers,
    )

    assert response.status_code == 200
    embedder.assert_not_called()
    db.session.remove()
    stored = db.session.get(JournalEntry, entry_id)
    assert stored.entry_date == old_date
    assert list(stored.embedding) == pytest.approx([0.25] * 1536)
