"""Test the real Flask/JWT endpoint while mocking only the RAG service."""

from datetime import timedelta
from unittest.mock import Mock

import pytest
from flask_jwt_extended import create_access_token

from ai_validation import AIResponseValidationError
from services import rag_service
from services.exceptions import ProviderError, ProviderTimeoutError


URL = "/analysis/long-term"
QUESTION = "How do creative hobbies affect my mood?"
RESULT = {
    "answer": "Painting helped you relax.",
    "patterns": [],
    "sources": [{"entry_id": 10, "date": "2026-01-01", "mood_tag": "Calm",
                 "mood_score": 7, "notes": "Painting helped me relax."}],
}


@pytest.fixture()
def analyzer(monkeypatch):
    mock = Mock(return_value=RESULT)
    monkeypatch.setattr(rag_service, "analyze_mood", mock)
    return mock


@pytest.mark.parametrize("headers,status", [
    ({}, 401),
    ({"Authorization": "Bearer invalid-token"}, 422),
])
def test_auth(client, analyzer, headers, status):
    response = client.post(URL, json={"question": QUESTION}, headers=headers)
    assert response.status_code == status
    analyzer.assert_not_called()


def test_expired(client, user_a, analyzer):
    token = create_access_token(identity=str(user_a.id), expires_delta=timedelta(seconds=-1))
    response = client.post(URL, json={"question": QUESTION}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    analyzer.assert_not_called()


@pytest.mark.parametrize("body", [None, [], "text", 42])
def test_bad_body(client, auth_headers, analyzer, body):
    response = client.post(URL, json=body, headers=auth_headers)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Request body must be a JSON object."}
    analyzer.assert_not_called()


def test_bad_json(client, auth_headers, analyzer):
    response = client.post(URL, data='{broken', content_type="application/json", headers=auth_headers)
    assert response.status_code == 400
    analyzer.assert_not_called()


@pytest.mark.parametrize("body", [
    {}, {"question": None}, {"question": ""}, {"question": " \n "},
    {"question": 12}, {"question": []}, {"question": {}},
])
def test_bad_question(client, auth_headers, analyzer, body):
    response = client.post(URL, json=body, headers=auth_headers)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Please select a question."}
    analyzer.assert_not_called()


@pytest.mark.parametrize("time_range", ["2_months", "", 123, [], {}])
def test_bad_range(client, auth_headers, analyzer, time_range):
    response = client.post(URL, json={"question": QUESTION, "time_range": time_range}, headers=auth_headers)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Unsupported time_range."}
    analyzer.assert_not_called()


@pytest.mark.parametrize("time_range", ["3_months", "6_months", "1_year", "all_time"])
def test_success(client, auth_headers, user_a, analyzer, time_range):
    response = client.post(
        URL, json={"question": f"  {QUESTION}  ", "time_range": time_range}, headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == RESULT
    analyzer.assert_called_once_with(
        user_id=str(user_a.id), question=QUESTION, time_range=time_range,
    )


@pytest.mark.parametrize("range_data", [{}, {"time_range": None}])
def test_default(client, auth_headers, user_a, analyzer, range_data):
    response = client.post(URL, json={"question": QUESTION, **range_data}, headers=auth_headers)
    assert response.status_code == 200
    analyzer.assert_called_once_with(
        user_id=str(user_a.id), question=QUESTION, time_range="3_months",
    )


def test_identity(client, auth_headers, user_a, user_b, analyzer):
    response = client.post(
        URL, json={"question": QUESTION, "user_id": user_b.id}, headers=auth_headers,
    )
    assert response.status_code == 200
    analyzer.assert_called_once_with(
        user_id=str(user_a.id), question=QUESTION, time_range="3_months",
    )


def test_empty(client, auth_headers, analyzer):
    analyzer.return_value = {
        "answer": "There is not enough journal evidence to answer this question.",
        "patterns": [], "sources": [],
    }
    response = client.post(URL, json={"question": QUESTION}, headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json() == analyzer.return_value


@pytest.mark.parametrize("error_type,status,message", [
    (ProviderTimeoutError, 504, "AI service timed out. Please try again."),
    (ProviderError, 502, "AI service could not complete the analysis."),
    (AIResponseValidationError, 502, "AI service returned an invalid response."),
    (RuntimeError, 500, "Could not complete the analysis."),
])
def test_errors(client, auth_headers, analyzer, error_type, status, message):
    analyzer.side_effect = error_type("Private provider details")
    response = client.post(URL, json={"question": QUESTION}, headers=auth_headers)
    assert response.status_code == status
    assert response.get_json() == {"error": message}
    assert "Private provider details" not in response.get_data(as_text=True)
    analyzer.assert_called_once()
