"""
This file contains the tests for the chatbot.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import


import time
from datetime import datetime, timedelta, timezone
from typing import Generator

import pytest
from model import Model, ModelMocked

import database as db
from chatbot import (
    Messages,
    _generate_text,
    _get_system_message,
    _parse_time,
    generate_event,
    response_cycle,
)
from tests.test_database.test_characters import char_1
from tests.test_database.test_events import event_1, event_2
from tests.test_database.test_main import db_init
from tests.test_database.test_threads import thread_1
from tests.test_database.test_users import user_1


@pytest.fixture
def model(db_init: str) -> Generator[Model, None, None]:
    """Yields a Model object for testing."""
    model = Model(ModelMocked("short"))
    yield model


def test_get_system_message(model: Model, thread_1: db.Thread) -> None:
    """
    Test the _get_system_message function.
    """
    system_message = _get_system_message("chat", thread_1)
    assert system_message["role"] == "system"
    assert "You are an expert actor who" in system_message["content"]
    system_message = _get_system_message("time", thread_1)
    assert system_message["role"] == "system"
    assert "current response frequency of" in system_message["content"]


def test_generate_text(model: Model, thread_1: db.Thread) -> None:
    """
    Test the get_response function.
    """
    assert thread_1["id"]
    system_message = _get_system_message("chat", thread_1)
    chatlog = Messages(thread_1["id"]).sorted()
    response = _generate_text(model, system_message, chatlog)

    assert response["role"] == "assistant"
    assert "Mock response" in response["content"]


def test_response_cycle_short(model: Model, thread_1: db.Thread) -> None:
    """
    Test the response cycle function when responses are short.
    """
    assert thread_1["id"]
    response_cycle(model, thread_1["id"])
    messages = db.select_messages_by_thread(thread_1["id"])
    assert messages[-1]["role"]
    assert messages[-1]["role"] == "assistant"
    assert messages[-1]["content"]
    assert "Mock response" in messages[-1]["content"]


def test_response_cycle_long(model: Model, thread_1: db.Thread) -> None:
    """
    Test the response cycle function when responses are long.
    """
    assert thread_1["id"]
    model = Model(ModelMocked("long"))
    response_cycle(model, thread_1["id"])
    messages = db.select_messages_by_thread(thread_1["id"])
    assert messages[-1]["role"] == "assistant"
    assert messages[-1]["content"]
    assert "Mock response" in messages[-1]["content"]
    assert messages[-1]["timestamp"]
    assert db.convert_ts_dt(messages[-1]["timestamp"]) > datetime.now(timezone.utc)


def test_response_cycle_repeated(model: Model, thread_1: db.Thread) -> None:
    """
    Test the response cycle function ensuring multiple responses aren't
    scheduled for repeated messages.
    """
    assert thread_1["id"]
    model = Model(ModelMocked("long"))
    response_cycle(model, thread_1["id"])
    response_cycle(model, thread_1["id"])
    time.sleep(10)
    messages = db.select_messages_by_thread(thread_1["id"])
    assert len(messages) == 1
    assert messages[-1]["role"] == "assistant"
    assert messages[-1]["content"] == "Mock response"


def test_parse_time() -> None:
    """
    Test the _parse_time function.
    """
    # Basic tests
    time = "1d 2h 3m 4s"
    assert _parse_time(time) == timedelta(days=1, hours=2, minutes=3, seconds=4)
    time = "2h 3m 4s"
    assert _parse_time(time) == timedelta(hours=2, minutes=3, seconds=4)
    time = "3m 4s"
    assert _parse_time(time) == timedelta(minutes=3, seconds=4)
    time = "1d 2h 3m"
    assert _parse_time(time) == timedelta(days=1, hours=2, minutes=3)
    time = "2h 3m"
    assert _parse_time(time) == timedelta(hours=2, minutes=3)
    time = "3m"
    assert _parse_time(time) == timedelta(minutes=3)
    time = "4s"
    assert _parse_time(time) == timedelta(seconds=4)

    # Messy tests
    time = "Sure. The time is: 2h30s"
    assert _parse_time(time) == timedelta(hours=2, seconds=30)
    time = "I would wait 5m and 16s"
    assert _parse_time(time) == timedelta(minutes=5, seconds=16)
    time = "1d3h and I think 22m"
    assert _parse_time(time) == timedelta(days=1, hours=3, minutes=22)
    time = "I would wait 55s no wait, 14s"  # Always take first
    assert _parse_time(time) == timedelta(seconds=55)
    time = "3m and 50s. What do you think?"
    assert _parse_time(time) == timedelta(minutes=3, seconds=50)
    time = "I can't wait!"
    assert _parse_time(time) == timedelta(seconds=0)


def test_generate_event(
    model: Model, char_1: db.Character, event_1: db.Event, event_2: db.Event
) -> None:
    """
    Test the generate_event function.
    """
    assert char_1["id"]
    generate_event(model, char_1["id"], "event")
    events = db.select_events(db.Event(character=char_1["id"]))
    assert len(events) == 3
    assert events[0]["content"] == "test event"
    assert events[0]["type"] == "event"
    assert events[1]["content"] == "test thought"
    assert events[1]["type"] == "thought"
    assert events[2]["content"] == "Mock event"
    assert events[2]["type"] == "event"
