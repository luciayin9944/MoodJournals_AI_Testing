from datetime import date

import pytest

from config import db
from models import Journal, JournalEntry


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
