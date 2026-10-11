"""Vector tests require TEST_DATABASE_URI for a disposable PostgreSQL database.

Enable the vector extension first. The shared app fixture creates and drops
application tables. SQLite runs the date/error tests and skips vector searches.
"""

from datetime import date, timedelta
from unittest.mock import Mock

import pytest

from config import db
from services import rag_service, retrieval_service
from services.exceptions import ProviderTimeoutError


TODAY = date(2026, 3, 31)
QUESTION = "What improves my mood?"


def vector(x, y=0):
    return [x, y] + [0.0] * 1534


@pytest.fixture(autouse=True)
def clock(monkeypatch):
    class FixedDate(date):
        @classmethod
        def today(cls):
            return TODAY

    monkeypatch.setattr(retrieval_service, "date", FixedDate)


@pytest.fixture()
def vectors(app, monkeypatch):
    if db.engine.dialect.name != "postgresql":
        pytest.skip("Vector search needs PostgreSQL with pgvector; set TEST_DATABASE_URI.")
    embedder = Mock(return_value=vector(1))
    generator = Mock(side_effect=AssertionError("Retrieval must not generate answers."))
    monkeypatch.setattr(retrieval_service, "generate_embedding", embedder)
    monkeypatch.setattr(rag_service, "generate_answer", generator)
    yield embedder
    generator.assert_not_called()


@pytest.fixture()
def add(vectors, make_entry):
    def create(user, day, x=1, y=0):
        entry = make_entry(user, entry_date=day)
        entry.embedding = vector(x, y)
        db.session.commit()
        return entry

    return create


@pytest.mark.parametrize("time_range,start", [
    ("3_months", date(2025, 12, 31)),
    ("6_months", date(2025, 9, 30)),
    ("1_year", date(2025, 3, 31)),
    ("all_time", None),
])
def test_ranges(time_range, start):
    assert retrieval_service.get_date_range(time_range) == (start, TODAY)


def test_leap(monkeypatch):
    class LeapDate(date):
        @classmethod
        def today(cls):
            return date(2024, 5, 31)

    monkeypatch.setattr(retrieval_service, "date", LeapDate)
    assert retrieval_service.get_date_range("3_months") == (
        date(2024, 2, 29), date(2024, 5, 31),
    )


def test_bad_range(monkeypatch):
    embedder = Mock()
    monkeypatch.setattr(retrieval_service, "generate_embedding", embedder)
    with pytest.raises(ValueError, match="Unsupported time_range"):
        retrieval_service.retrieval_entries(1, QUESTION, "2_months")
    embedder.assert_not_called()


def test_embed_error(monkeypatch):
    embedder = Mock(side_effect=ProviderTimeoutError("Timed out"))
    monkeypatch.setattr(retrieval_service, "generate_embedding", embedder)
    with pytest.raises(ProviderTimeoutError):
        retrieval_service.retrieval_entries(1, QUESTION, "all_time")
    embedder.assert_called_once_with(QUESTION)


def test_user(add, user_a, user_b):
    # Another user's closer match must not displace this user's entry.
    add(user_b, TODAY)
    own = add(user_a, TODAY, 1, 1)
    result = retrieval_service.retrieval_entries(user_a.id, QUESTION, "all_time", top_k=1)
    assert [entry.id for entry in result] == [own.id]


@pytest.mark.parametrize("time_range,start", [
    ("3_months", date(2025, 12, 31)),
    ("6_months", date(2025, 9, 30)),
    ("1_year", date(2025, 3, 31)),
])
def test_dates(add, user_a, time_range, start):
    add(user_a, start - timedelta(days=1))
    first = add(user_a, start)
    last = add(user_a, TODAY)
    add(user_a, TODAY + timedelta(days=1))
    result = retrieval_service.retrieval_entries(user_a.id, QUESTION, time_range)
    assert {entry.id for entry in result} == {first.id, last.id}


def test_all_time(add, user_a):
    old = add(user_a, date(2000, 1, 1))
    current = add(user_a, TODAY)
    add(user_a, TODAY + timedelta(days=1))
    result = retrieval_service.retrieval_entries(user_a.id, QUESTION, "all_time")
    assert {entry.id for entry in result} == {old.id, current.id}


def test_null(add, make_entry, user_a):
    make_entry(user_a, entry_date=TODAY)
    embedded = add(user_a, TODAY - timedelta(days=1))
    result = retrieval_service.retrieval_entries(user_a.id, QUESTION, "all_time")
    assert [entry.id for entry in result] == [embedded.id]


def test_top_k(add, vectors, user_a):
    # Insert out of similarity order; PostgreSQL must rank the actual vectors.
    add(user_a, TODAY, 0, 1)
    middle = add(user_a, TODAY - timedelta(days=1), 1, 1)
    nearest = add(user_a, TODAY - timedelta(days=2), 1, 0)
    result = retrieval_service.retrieval_entries(user_a.id, QUESTION, "all_time", top_k=2)
    assert [entry.id for entry in result] == [nearest.id, middle.id]
    vectors.assert_called_once_with(QUESTION)


def test_ties(add, user_a):
    first = add(user_a, TODAY)
    second = add(user_a, TODAY - timedelta(days=1))
    result = retrieval_service.retrieval_entries(user_a.id, QUESTION, "all_time")
    assert [entry.id for entry in result] == [first.id, second.id]


def test_default_k(add, user_a):
    entries = [add(user_a, TODAY - timedelta(days=i), 1, i / 12) for i in range(12)]
    result = retrieval_service.retrieval_entries(user_a.id, QUESTION, "all_time")
    assert [entry.id for entry in result] == [entry.id for entry in entries[:10]]


def test_empty(vectors, user_a):
    assert retrieval_service.retrieval_entries(user_a.id, QUESTION, "all_time") == []
