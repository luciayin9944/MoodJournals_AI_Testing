"""Embedding text, request, and response contracts without live provider calls."""

from datetime import date
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from flask import Flask
from openai import OpenAI

from config import Config
from models import JournalEntry
from services import embedding_service, openai_client
from services.exceptions import (
    ProviderConfigurationError,
    ProviderRequestError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)


@pytest.fixture()
def entry():
    return JournalEntry(
        id=42,
        journal_id=99,
        entry_date=date(2026, 9, 24),
        mood_tag="Anxious",
        mood_score=4,
        notes="  I didn't sleep for 2 hours. 😟\nA walk helped.  ",
    )


@pytest.fixture()
def ctx():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["OPENAI_API_KEY"] = "test-key"
    with app.app_context():
        yield app


@pytest.fixture()
def provider(monkeypatch, ctx):
    client = Mock()
    client.embeddings.create.return_value = SimpleNamespace(
        data=[SimpleNamespace(embedding=[0.125] * 1536)]
    )
    call = Mock(side_effect=lambda operation: operation(client))
    monkeypatch.setattr(embedding_service, "call_openai", call)
    return SimpleNamespace(client=client, call=call)


def test_entry_text(entry):
    assert embedding_service.build_entry_embedding_text(entry) == (
        "Mood tag: Anxious\nMood score: 4/10\n"
        "Notes: I didn't sleep for 2 hours. 😟\nA walk helped."
    )


@pytest.mark.parametrize("notes", [None, "", " \n\t "])
def test_empty_notes(entry, notes):
    entry.notes = notes
    assert embedding_service.build_entry_embedding_text(entry) == (
        "Mood tag: Anxious\nMood score: 4/10"
    )


def test_default_tag():
    entry = JournalEntry(mood_score=6, notes=None)
    assert embedding_service.build_entry_embedding_text(entry) == (
        "Mood tag: Other\nMood score: 6/10"
    )


@pytest.mark.parametrize("notes", [[], {}, 0, False])
def test_bad_notes(entry, notes):
    entry.notes = notes
    with pytest.raises(ValueError, match="Entry notes"):
        embedding_service.build_entry_embedding_text(entry)


def test_metadata_excluded(entry):
    original = embedding_service.build_entry_embedding_text(entry)
    entry.id = 123
    entry.journal_id = 456
    entry.entry_date = date(2025, 1, 1)
    assert embedding_service.build_entry_embedding_text(entry) == original


def test_generate(provider):
    question = "What situations usually make me feel anxious?"
    result = embedding_service.generate_embedding(f"  {question}\n")

    provider.client.embeddings.create.assert_called_once_with(
        model="text-embedding-3-small", dimensions=1536,
        input=question, encoding_format="float",
    )
    assert result == [0.125] * 1536
    assert all(isinstance(value, float) for value in result)


def test_entry_embedding(provider, entry):
    result = embedding_service.generate_entry_embedding(entry)

    assert result == [0.125] * 1536
    assert provider.client.embeddings.create.call_args.kwargs["input"] == (
        "Mood tag: Anxious\nMood score: 4/10\n"
        "Notes: I didn't sleep for 2 hours. 😟\nA walk helped."
    )


def test_entry_unchanged(provider, entry):
    old_embedding = [0.25] * 1536
    entry.embedding = old_embedding
    notes = entry.notes

    embedding_service.generate_entry_embedding(entry)

    assert entry.embedding is old_embedding
    assert entry.notes == notes


@pytest.mark.parametrize("text", [None, "", " \n ", ["some", "words"], 123, False])
def test_invalid_text(provider, text):
    with pytest.raises(ValueError, match="non-empty string"):
        embedding_service.generate_embedding(text)
    provider.call.assert_not_called()


@pytest.mark.parametrize("setting,value", [
    ("EMBEDDING_MODEL", "text-embedding-3-large"),
    ("EMBEDDING_MODEL", None),
    ("EMBEDDING_DIMENSIONS", 3072),
    ("EMBEDDING_DIMENSIONS", "1536"),
    ("EMBEDDING_DIMENSIONS", 1536.0),
    ("EMBEDDING_DIMENSIONS", True),
])
def test_bad_config(provider, ctx, setting, value):
    ctx.config[setting] = value
    with pytest.raises(ProviderConfigurationError):
        embedding_service.generate_embedding("Example text.")
    provider.call.assert_not_called()


@pytest.mark.parametrize("response", [
    None,
    SimpleNamespace(),
    SimpleNamespace(data=None),
    SimpleNamespace(data={}),
    SimpleNamespace(data=[]),
    SimpleNamespace(data=[None]),
    SimpleNamespace(data=[SimpleNamespace()]),
    SimpleNamespace(data=[SimpleNamespace(embedding="not a vector")]),
    SimpleNamespace(data=[SimpleNamespace(embedding=None)]),
    SimpleNamespace(data=[SimpleNamespace(embedding=[0.1] * 1536)] * 2),
])
def test_bad_response(provider, response):
    provider.client.embeddings.create.return_value = response
    with pytest.raises(ProviderResponseError):
        embedding_service.generate_embedding("Example text.")
    assert provider.call.call_count == 1


@pytest.mark.parametrize("size", [0, 1535, 1537])
def test_wrong_size(provider, size):
    provider.client.embeddings.create.return_value.data[0].embedding = [0.1] * size
    with pytest.raises(ProviderResponseError, match="size"):
        embedding_service.generate_embedding("Example text.")


@pytest.mark.parametrize("error_type", [
    ProviderTimeoutError, ProviderUnavailableError,
    ProviderConfigurationError, ProviderRequestError,
])
def test_provider_error(provider, error_type):
    error = error_type("Controlled provider failure.")
    provider.call.side_effect = error
    with pytest.raises(error_type) as caught:
        embedding_service.generate_embedding("Example text.")
    assert caught.value is error
    assert provider.call.call_count == 1


def test_sdk_empty_result(ctx, monkeypatch):
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json={
            "object": "list", "model": "text-embedding-3-small", "data": [],
            "usage": {"prompt_tokens": 1, "total_tokens": 1},
        })

    def client(**kwargs):
        return OpenAI(
            **kwargs, http_client=httpx.Client(transport=httpx.MockTransport(handle))
        )

    monkeypatch.setattr(openai_client, "OpenAI", client)
    with pytest.raises(ProviderResponseError, match="exactly one"):
        embedding_service.generate_embedding("Example text.")
    assert len(requests) == 1
