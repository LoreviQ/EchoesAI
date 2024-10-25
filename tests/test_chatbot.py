"""
This file contains the tests for the chatbot.py file.
"""

# pylint: disable=redefined-outer-name, protected-access
import os
from datetime import datetime, timedelta, timezone
from typing import Generator, Tuple

import pytest

import database as db
from chatbot import (
    Events,
    Messages,
    _generate_text,
    _get_system_message,
    _parse_time,
    generate_event,
    generate_social_media_post,
    response_cycle,
)
from model import Model, ModelMocked


@pytest.fixture
def args(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[Tuple[Model, db.Character, db.Thread], None, None]:
    """
    Setup the database and teardown after testing, yielding args for tests
    """
    test_name = os.environ.get("PYTEST_CURRENT_TEST")
    if test_name is None:
        test_name = "unknown"
    else:
        test_name = test_name.split(":")[-1].split(" ")[0]
    db_path = f"test_database_{test_name}.db"
    monkeypatch.setattr("database.main.DB_PATH", db_path)
    db.create_db()
    character_id = db.insert_character(
        db.Character(
            name="test character",
            path_name="test_character",
            initial_message="test initial message",
        )
    )
    character = db.select_character(character_id)
    thread_id = db.insert_thread("test user", character_id)
    thread = db.select_thread(thread_id)
    db.insert_message(
        db.Message(
            thread=thread,
            content="test message",
            role="user",
            timestamp=datetime.now(timezone.utc),
        )
    )
    model = Model(ModelMocked("short"))
    yield model, character, thread
    os.remove(db_path)


def test_get_system_message(args: Tuple[Model, db.Character, db.Thread]) -> None:
    """
    Test the _get_system_message function.
    """
    system_message = _get_system_message("chat", args[2])
    assert system_message["role"] == "system"
    assert "You are an expert actor who" in system_message["content"]
    system_message = _get_system_message("time", args[2])
    assert system_message["role"] == "system"
    assert "current response frequency of" in system_message["content"]


def test_generate_text(args: Tuple[Model, db.Character, db.Thread]) -> None:
    """
    Test the get_response function.
    """
    assert args[2]["id"]
    system_message = _get_system_message("chat", args[2])
    chatlog = Messages(args[2]["id"]).sorted()
    response = _generate_text(args[0], system_message, chatlog)

    assert response["role"] == "assistant"
    assert "Mock response" in response["content"]


def test_response_cycle_short(args: Tuple[Model, db.Character, db.Thread]) -> None:
    """
    Test the response cycle function when responses are short.
    """
    assert args[2]["id"]
    response_cycle(args[0], args[2]["id"])
    messages = db.select_messages_by_thread(args[2]["id"])
    assert messages[-1]["role"]
    assert messages[-1]["role"] == "assistant"
    assert messages[-1]["content"]
    assert "Mock response" in messages[-1]["content"]


def test_response_cycle_long(args: Tuple[Model, db.Character, db.Thread]) -> None:
    """
    Test the response cycle function when responses are long.
    """
    assert args[2]["id"]
    model = Model(ModelMocked("long"))
    response_cycle(model, args[2]["id"])
    messages = db.select_messages_by_thread(args[2]["id"])
    assert messages[-1]["role"] == "assistant"
    assert messages[-1]["content"]
    assert "Mock response" in messages[-1]["content"]
    assert messages[-1]["timestamp"]
    assert messages[-1]["timestamp"] > datetime.now(timezone.utc)


def test_response_cycle_single(args: Tuple[Model, db.Character, db.Thread]) -> None:
    """
    Tests that a single response is scheduled at one time.
    """
    assert args[2]["id"]
    response_cycle(args[0], args[2]["id"])
    response_cycle(args[0], args[2]["id"])
    messages = db.select_messages_by_thread(args[2]["id"])
    assert len(messages) == 3
    assert messages[0]["role"] == "assistant"
    assert messages[-1]["role"] == "assistant"


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


def test_generate_event(args: Tuple[Model, db.Character, db.Thread]) -> None:
    """
    Test the generate_event function.
    """
    assert args[1]["id"]
    mock_event = db.Event(
        character=args[1]["id"],
        type="event",
        content="test was drinking tea",
    )
    mock_thought = db.Event(
        character=args[1]["id"],
        type="thought",
        content="test thought about the sky",
    )
    db.insert_event(mock_event)
    db.insert_event(mock_thought)
    generate_event(args[0], args[1]["id"], "event")
    events = db.select_events_by_character(args[1]["id"])
    assert len(events) == 3
    assert events[0]["content"] == "test was drinking tea"
    assert events[0]["type"] == "event"
    assert events[1]["content"] == "test thought about the sky"
    assert events[1]["type"] == "thought"
    assert events[2]["content"] == "Mock event"
    assert events[2]["type"] == "event"
