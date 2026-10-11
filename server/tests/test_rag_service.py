"""Test RAG orchestration with real entry records and mocked provider calls."""

import json
from datetime import date
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from ai_validation import AIResponseValidationError
from services import rag_service
from services.exceptions import ProviderError, ProviderTimeoutError


QUESTION = "What improves my mood?"
ANSWER = {"answer": "Walking and talking with friends helped.", "patterns": []}


@pytest.fixture()
def entries(make_entry, user_a):
    return [
        make_entry(user_a, date(2026, 1, 1), 7, "Calm", "A walk helped me relax."),
        make_entry(user_a, date(2026, 1, 2), 8, "Happy", "A friend listened to my worries."),
    ]


@pytest.fixture()
def provider(monkeypatch):
    message = SimpleNamespace(content=json.dumps(ANSWER))
    client = Mock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=message)],
    )
    call = Mock(side_effect=lambda operation: operation(client))
    monkeypatch.setattr(rag_service, "call_openai", call)
    return SimpleNamespace(client=client, message=message, call=call)


@pytest.fixture()
def retrieve(monkeypatch, entries):
    mock = Mock(return_value=entries)
    monkeypatch.setattr(rag_service, "retrieval_entries", mock)
    return mock


def test_context(entries):
    context = rag_service.build_context(entries)
    for entry in entries:
        assert f"Entry ID: {entry.id}" in context
        assert entry.entry_date.isoformat() in context
        assert entry.mood_tag in context
        assert f"Score: {entry.mood_score}/10" in context
        assert entry.notes in context
    assert context.index(entries[0].notes) < context.index(entries[1].notes)


def test_empty_notes(entries):
    entries[0].notes = None
    context = rag_service.build_context(entries[:1])
    assert "Notes: " in context
    assert "None" not in context
    assert rag_service.build_sources(entries[:1])[0]["notes"] is None


def test_sources(entries):
    sources = rag_service.build_sources(entries)
    assert sources == [
        {"entry_id": entries[0].id, "date": "2026-01-01", "mood_tag": "Calm",
         "mood_score": 7, "notes": "A walk helped me relax."},
        {"entry_id": entries[1].id, "date": "2026-01-02", "mood_tag": "Happy",
         "mood_score": 8, "notes": "A friend listened to my worries."},
    ]


def test_prompt(app, entries, provider):
    app.config["RAG_GENERATION_MODEL"] = "test-model"
    assert rag_service.generate_answer(QUESTION, entries) == ANSWER
    provider.call.assert_called_once()
    provider.client.chat.completions.create.assert_called_once()
    request = provider.client.chat.completions.create.call_args.kwargs
    assert request["model"] == "test-model"
    prompt = request["messages"][1]["content"]
    assert QUESTION in prompt
    for entry in entries:
        assert entry.notes in prompt
    for rule in (
        "using only the supplied journal evidence",
        "Do not invent",
        "multiple distinct",
        "insufficient or unrelated",
        "Do not diagnose",
        "Do not include a sources field",
    ):
        assert rule in prompt


def test_analyze(user_a, make_entry, entries, retrieve, provider):
    unseen = make_entry(user_a, date(2026, 1, 3), notes="This entry was not retrieved.")
    # Even if the model invents sources, the application must use DB records.
    provider.message.content = json.dumps({
        **ANSWER, "sources": [{"entry_id": unseen.id, "notes": "Invented source"}],
    })
    result = rag_service.analyze_mood(user_a.id, QUESTION, "6_months", top_k=4)
    retrieve.assert_called_once_with(
        user_id=user_a.id, question=QUESTION, time_range="6_months", top_k=4,
    )
    assert result["answer"] == ANSWER["answer"]
    assert result["patterns"] == []
    assert [source["entry_id"] for source in result["sources"]] == [e.id for e in entries]
    assert [source["notes"] for source in result["sources"]] == [e.notes for e in entries]
    prompt = provider.client.chat.completions.create.call_args.kwargs["messages"][1]["content"]
    assert unseen.notes not in prompt
    assert "Invented source" not in json.dumps(result)


def test_empty(user_a, retrieve, provider):
    retrieve.return_value = []
    result = rag_service.analyze_mood(user_a.id, QUESTION, "all_time")
    assert result == {
        "answer": "There is not enough journal evidence to answer this question.",
        "patterns": [], "sources": [],
    }
    retrieve.assert_called_once_with(
        user_id=user_a.id, question=QUESTION, time_range="all_time", top_k=10,
    )
    provider.call.assert_not_called()


def test_sparse(user_a, entries, retrieve, provider):
    retrieve.return_value = entries[:1]
    answer = {"answer": "One walk helped, but there is not enough evidence for a recurring pattern.", "patterns": []}
    provider.message.content = json.dumps(answer)
    result = rag_service.analyze_mood(user_a.id, QUESTION, "3_months")
    assert result["answer"] == answer["answer"]
    assert result["patterns"] == []
    assert [source["entry_id"] for source in result["sources"]] == [entries[0].id]


@pytest.mark.parametrize("content", [None, "", "not JSON"])
def test_bad_response(entries, provider, content):
    provider.message.content = content
    with pytest.raises(AIResponseValidationError):
        rag_service.generate_answer(QUESTION, entries)


@pytest.mark.parametrize("stage", ["retrieval", "generation"])
@pytest.mark.parametrize("error_type", [ProviderError, ProviderTimeoutError])
def test_failures(user_a, retrieve, provider, stage, error_type):
    failure = error_type("Provider failed")
    if stage == "retrieval":
        retrieve.side_effect = failure
    else:
        provider.call.side_effect = failure
    with pytest.raises(error_type) as caught:
        rag_service.analyze_mood(user_a.id, QUESTION, "all_time")
    assert caught.value is failure
    if stage == "retrieval":
        provider.call.assert_not_called()
    else:
        provider.call.assert_called_once()
