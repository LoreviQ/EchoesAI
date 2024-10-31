"""Tests for the events module in the database package."""

# pylint: disable=redefined-outer-name unused-argument unused-import

import time
from typing import List

import database as db

from .fixtures import character, characters
from .test_main import test_db


def test_insert_event(character: db.Character) -> None:
    """Test the insert_event function."""
    event = db.Event(
        char_id=character["id"],
        type="event",
        content="test event",
    )
    result = db.insert_event(event)
    assert result == 1


def test_select_events_without_query(characters: List[db.Character]) -> None:
    """Test the select_events function without a query."""
    event = db.Event(
        char_id=characters[0]["id"],
        type="event",
        content="test event",
    )
    event2 = db.Event(
        char_id=characters[1]["id"],
        type="thought",
        content="test thought",
    )
    db.insert_event(event)
    db.insert_event(event2)
    result = db.select_events()
    assert len(result) == 2
    assert result[0]["type"] == "event"
    assert result[1]["type"] == "thought"


def test_select_events_with_query(characters: List[db.Character]) -> None:
    """Test the select_events with a query specifying a character."""
    event = db.Event(
        char_id=characters[0]["id"],
        type="event",
        content="test event",
    )
    event2 = db.Event(
        char_id=characters[1]["id"],
        type="thought",
        content="test thought",
    )
    event3 = db.Event(
        char_id=characters[0]["id"],
        type="thought",
        content="test thought 2",
    )
    db.insert_event(event)
    db.insert_event(event2)
    db.insert_event(event3)
    result = db.select_events(db.Event(char_id=characters[0]["id"]))
    assert len(result) == 2
    assert result[0]["type"] == "event"
    assert result[1]["type"] == "thought"


def test_select_events_with_query_no_matching(characters: List[db.Character]) -> None:
    """Test the select_characters function with a query that doesn't match any characters."""
    event = db.Event(
        char_id=characters[0]["id"],
        type="event",
        content="test event",
    )
    event2 = db.Event(
        char_id=characters[1]["id"],
        type="thought",
        content="test thought",
    )
    db.insert_event(event)
    db.insert_event(event2)
    result = db.select_events(db.Event(char_id=characters[2]["id"]))
    assert not result


def test_select_most_recent_event(character: db.Character) -> None:
    """Test the select_most_recent_event function."""
    event = db.Event(
        char_id=character["id"],
        type="event",
        content="test event",
    )
    event2 = db.Event(
        char_id=character["id"],
        type="thought",
        content="test thought",
    )
    db.insert_event(event)
    time.sleep(1)
    db.insert_event(event2)
    result = db.select_most_recent_event(character["id"])
    assert result["type"] == "thought"
    assert result["content"] == "test thought"
    assert result["char_id"] == character["id"]
    assert result["id"] == 2
    assert result["timestamp"]


def test_delete_event(character: db.Character) -> None:
    """Test the delete_event function."""
    event = db.Event(
        char_id=character["id"],
        type="event",
        content="test event",
    )
    event_id = db.insert_event(event)
    db.delete_event(event_id)
    result = db.select_events()
    assert not result
