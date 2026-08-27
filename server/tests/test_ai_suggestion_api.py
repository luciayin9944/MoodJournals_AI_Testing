import json
from types import SimpleNamespace

from config import db
from models import Suggestion


class FakeCompletions:
    def __init__(self, content=None, error=None):
        self.content = content
        self.error = error
        self.call_count = 0

    def create(self, **kwargs):
        self.call_count += 1
        if self.error:
            raise self.error
        message = SimpleNamespace(content=self.content)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def fake_ai_client(completions):
    return SimpleNamespace(chat=SimpleNamespace(completions=completions))


def _week_path(entry):
    iso_year, iso_week, _ = entry.entry_date.isocalendar()
    return f"/journals/{iso_year}/{iso_week}/suggestion"


def test_ai_suggestion_requires_four_entries(
    client, auth_headers, make_entry, user_a, current_week_dates, monkeypatch
):
    entries = [make_entry(user_a, entry_date) for entry_date in current_week_dates[:3]]
    completions = FakeCompletions(content="should not be used")
    monkeypatch.setattr(
        "resources.ai_suggestion.get_ai_client",
        lambda: fake_ai_client(completions),
    )

    response = client.post(_week_path(entries[0]), headers=auth_headers)

    assert response.status_code == 400
    assert "minimum 4 required" in response.get_json()["message"]
    assert completions.call_count == 0


def test_ai_suggestion_saves_mocked_provider_response(
    client, auth_headers, make_entry, user_a, current_week_dates, monkeypatch
):
    entries = [make_entry(user_a, entry_date) for entry_date in current_week_dates[:4]]
    provider_result = {
        "summary": "The week became calmer and more productive.",
        "self_care_tips": [
            "Keep a consistent sleep routine.",
            "Take a short walk after work.",
            "Reflect on one positive moment each day.",
        ],
    }
    completions = FakeCompletions(content=json.dumps(provider_result))
    monkeypatch.setattr(
        "resources.ai_suggestion.get_ai_client",
        lambda: fake_ai_client(completions),
    )

    response = client.post(_week_path(entries[0]), headers=auth_headers)

    assert response.status_code == 201
    body = response.get_json()
    assert body["summary"] == provider_result["summary"]
    assert json.loads(body["selfcare_tips"]) == provider_result["self_care_tips"]
    assert Suggestion.query.count() == 1
    assert completions.call_count == 1


def test_ai_suggestion_returns_controlled_provider_failure(
    client, auth_headers, make_entry, user_a, current_week_dates, monkeypatch
):
    entries = [make_entry(user_a, entry_date) for entry_date in current_week_dates[:4]]
    completions = FakeCompletions(error=RuntimeError("secret provider detail"))
    monkeypatch.setattr(
        "resources.ai_suggestion.get_ai_client",
        lambda: fake_ai_client(completions),
    )

    response = client.post(_week_path(entries[0]), headers=auth_headers)

    assert response.status_code == 500
    assert response.get_json()["error"] == "OpenAI API request failed."
    assert "secret provider detail" not in response.get_data(as_text=True)


def test_invalid_ai_response_is_not_saved(
    client, auth_headers, make_entry, user_a, current_week_dates, monkeypatch
):
    entries = [make_entry(user_a, entry_date) for entry_date in current_week_dates[:4]]
    invalid_result = {
        "summary": "A summary with the wrong number of tips.",
        "self_care_tips": ["Only one tip."],
    }
    completions = FakeCompletions(content=json.dumps(invalid_result))
    monkeypatch.setattr(
        "resources.ai_suggestion.get_ai_client",
        lambda: fake_ai_client(completions),
    )

    response = client.post(_week_path(entries[0]), headers=auth_headers)

    assert response.status_code == 500
    assert response.get_json()["error"] == (
        "AI response did not match the required format."
    )
    assert Suggestion.query.count() == 0


def test_unsafe_ai_response_is_not_saved(
    client, auth_headers, make_entry, user_a, current_week_dates, monkeypatch
):
    entries = [make_entry(user_a, entry_date) for entry_date in current_week_dates[:4]]
    unsafe_result = {
        "summary": "You definitely have clinical depression.",
        "self_care_tips": [
            "Take a short walk.",
            "Keep a regular sleep routine.",
            "Write down how you feel.",
        ],
    }
    completions = FakeCompletions(content=json.dumps(unsafe_result))
    monkeypatch.setattr(
        "resources.ai_suggestion.get_ai_client",
        lambda: fake_ai_client(completions),
    )

    response = client.post(_week_path(entries[0]), headers=auth_headers)

    assert response.status_code == 500
    assert response.get_json()["error"] == (
        "AI response did not pass deterministic content checks."
    )
    assert Suggestion.query.count() == 0


def test_existing_ai_suggestion_is_returned_without_provider_call(
    client, auth_headers, make_entry, user_a, current_week_dates, monkeypatch
):
    entry = make_entry(user_a, current_week_dates[0])
    saved = Suggestion(
        journal_id=entry.journal_id,
        summary="Previously generated summary.",
        selfcare_tips=json.dumps(["Tip one", "Tip two", "Tip three"]),
    )
    db.session.add(saved)
    db.session.commit()
    completions = FakeCompletions(error=AssertionError("provider should not be called"))
    monkeypatch.setattr(
        "resources.ai_suggestion.get_ai_client",
        lambda: fake_ai_client(completions),
    )

    response = client.post(_week_path(entry), headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json()["summary"] == "Previously generated summary."
    assert completions.call_count == 0
