"""Exercise provider reliability through the real SDK and a mocked HTTP transport."""

from types import SimpleNamespace

import httpx
import pytest
from flask import Flask
from openai import OpenAI, OpenAIError
from openai import _base_client

from services import openai_client
from services.exceptions import (
    ProviderConfigurationError,
    ProviderError,
    ProviderRequestError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)


def ok():
    return httpx.Response(200, json={
        "object": "list",
        "model": "test-model",
        "data": [{"object": "embedding", "index": 0, "embedding": [0.25]}],
        "usage": {"prompt_tokens": 1, "total_tokens": 1},
    })


def fail(status, code=None, headers=None):
    return httpx.Response(status, headers=headers, json={
        "error": {
            "message": "sensitive provider details",
            "type": "api_error",
            "code": code,
        },
    })


def call():
    return openai_client.call_openai(
        lambda client: client.embeddings.create(model="test-model", input="fixture")
    )


@pytest.fixture()
def ctx():
    app = Flask(__name__)
    app.config.update(
        OPENAI_API_KEY="test-key",
        OPENAI_TIMEOUT_SECONDS=7.5,
        OPENAI_MAX_RETRIES=2,
    )
    with app.app_context():
        yield app


@pytest.fixture()
def provider(monkeypatch, ctx):
    def setup(*events):
        state = SimpleNamespace(requests=[], clients=[], settings=[], delays=[])
        events = iter(events)

        def handle(request):
            state.requests.append(request)
            event = next(events)
            if isinstance(event, Exception):
                raise event
            return event

        def build(**kwargs):
            state.settings.append(kwargs)
            client = OpenAI(
                **kwargs,
                http_client=httpx.Client(transport=httpx.MockTransport(handle)),
            )
            state.clients.append(client)
            return client

        monkeypatch.setattr(openai_client, "OpenAI", build)
        monkeypatch.setattr(_base_client.time, "sleep", state.delays.append)
        monkeypatch.setattr(_base_client, "random", lambda: 0)
        return state

    return setup


def test_client_setup(provider):
    state = provider(ok())

    result = call()

    assert result.data[0].embedding == [0.25]
    assert len(state.requests) == 1
    assert state.settings[0]["timeout"] == 7.5
    assert state.settings[0]["max_retries"] == 2
    assert state.requests[0].extensions["timeout"] == {
        "connect": 7.5, "read": 7.5, "write": 7.5, "pool": 7.5,
    }
    assert state.delays == []
    assert state.clients[0].is_closed()


@pytest.mark.parametrize("status", [408, 429, 500, 503])
def test_status_retry(provider, status):
    state = provider(fail(status), ok())

    assert call().data[0].embedding == [0.25]
    assert len(state.requests) == 2
    assert state.delays == [0.5]


@pytest.mark.parametrize("error_type", [httpx.ReadTimeout, httpx.ConnectError])
def test_network_retry(provider, error_type):
    state = provider(error_type("sensitive transport details"), ok())

    call()

    assert len(state.requests) == 2
    assert state.delays == [0.5]


@pytest.mark.parametrize("timeout", [False, True])
def test_retry_limit(provider, timeout):
    events = [httpx.ReadTimeout("sensitive timeout") if timeout else fail(503)
              for _ in range(3)]
    state = provider(*events)
    expected = ProviderTimeoutError if timeout else ProviderUnavailableError

    with pytest.raises(expected) as caught:
        call()

    assert len(state.requests) == 3
    assert state.delays == [0.5, 1.0]
    assert "sensitive" not in str(caught.value)
    assert isinstance(caught.value.__cause__, OpenAIError)
    assert state.clients[0].is_closed()


@pytest.mark.parametrize("status,code,expected", [
    (400, None, ProviderRequestError),
    (401, None, ProviderConfigurationError),
    (403, None, ProviderConfigurationError),
    (404, "model_not_found", ProviderConfigurationError),
    (422, None, ProviderRequestError),
    (400, "model_not_found", ProviderConfigurationError),
])
def test_permanent_error(provider, status, code, expected):
    state = provider(fail(status, code))

    with pytest.raises(expected) as caught:
        call()

    assert len(state.requests) == 1
    assert state.delays == []
    assert "sensitive" not in str(caught.value)
    assert state.clients[0].is_closed()


def test_no_retries(provider, ctx):
    ctx.config["OPENAI_MAX_RETRIES"] = 0
    state = provider(fail(503))

    with pytest.raises(ProviderUnavailableError):
        call()

    assert len(state.requests) == 1
    assert state.delays == []


@pytest.mark.parametrize("code", [
    "insufficient_quota", "billing_hard_limit_reached", "billing_not_active",
])
def test_quota_error(provider, code):
    state = provider(*(fail(429, code) for _ in range(3)))

    with pytest.raises(ProviderConfigurationError) as caught:
        call()

    assert len(state.requests) == 3
    assert "sensitive" not in str(caught.value)
    assert state.clients[0].is_closed()


def test_retry_after(provider):
    state = provider(fail(429, headers={"retry-after": "2"}), ok())

    call()

    assert len(state.requests) == 2
    assert state.delays == [2.0]


@pytest.mark.parametrize("setting,value", [
    ("OPENAI_API_KEY", None),
    ("OPENAI_API_KEY", "   "),
    ("OPENAI_TIMEOUT_SECONDS", 0),
    ("OPENAI_TIMEOUT_SECONDS", -1),
    ("OPENAI_TIMEOUT_SECONDS", float("nan")),
    ("OPENAI_TIMEOUT_SECONDS", float("inf")),
    ("OPENAI_MAX_RETRIES", -1),
])
def test_invalid_config(
    provider, ctx, setting, value
):
    ctx.config[setting] = value
    state = provider()

    with pytest.raises(ProviderConfigurationError, match=setting):
        call()

    assert state.clients == []
    assert state.requests == []


def test_sdk_error(provider):
    state = provider()

    def op(client):
        raise OpenAIError("sensitive provider details")

    with pytest.raises(ProviderError, match="^AI provider request failed\\.$"):
        openai_client.call_openai(op)

    assert state.delays == []
    assert state.clients[0].is_closed()


def test_code_error(provider):
    state = provider()

    def op(client):
        raise TypeError("invalid local operation")

    with pytest.raises(TypeError, match="invalid local operation"):
        openai_client.call_openai(op)

    assert state.delays == []
    assert state.clients[0].is_closed()
