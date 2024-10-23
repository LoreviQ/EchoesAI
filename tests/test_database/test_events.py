"""
This file contains the tests for the database/threads.py file.
"""

import os
import time
from typing import Generator, Tuple

import pytest

import database as db

# pylint: disable=redefined-outer-name unused-argument unused-import


@pytest.fixture
def chars(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[Tuple[db.Character, db.Character], None, None]:
    """
    Create a DB object for testing and teardown after testing.
    """
    test_name = os.environ.get("PYTEST_CURRENT_TEST")
    if test_name is None:
        test_name = "unknown"
    else:
        test_name = test_name.split(":")[-1].split(" ")[0]
    db_path = f"test_database_{test_name}.db"
    monkeypatch.setattr("database.main.DB_PATH", db_path)
    db.create_db()
    character_1 = db.Character(name="test character", path_name="test_character")
    character_1["id"] = db.insert_character(character_1)
    character_2 = db.Character(name="test character 2", path_name="test_character_2")
    character_2["id"] = db.insert_character(character_2)
    yield character_1, character_2
    os.remove(db_path)


def test_insert_event(chars: Tuple[db.Character, db.Character]) -> None:
    """
    Test the insert_event function.
    """
    event1 = db.Event(
        character=chars[0]["id"],
        type="event",
        content="test event",
    )
    event2 = db.Event(
        character=chars[1]["id"],
        type="thought",
        content="test thought",
    )
    event1_id = db.events.insert_event(event1)
    event2_id = db.events.insert_event(event2)
    assert event1_id == 1
    assert event2_id == 2


def test_select_events_by_character(chars: Tuple[db.Character, db.Character]) -> None:
    """
    Test the select_events_by_character function.
    """
    assert chars[0]["id"]
    assert chars[1]["id"]
    event1 = db.Event(
        character=chars[0]["id"],
        type="event",
        content="test event",
    )
    event2 = db.Event(
        character=chars[1]["id"],
        type="thought",
        content="test thought",
    )
    event3 = db.Event(
        character=chars[0]["id"],
        type="thought",
        content="test thought 2",
    )
    db.events.insert_event(event1)
    db.events.insert_event(event2)
    db.events.insert_event(event3)
    events = db.events.select_events_by_character(chars[0]["id"])
    assert len(events) == 2
    assert events[0]["type"] == "event"
    assert events[1]["type"] == "thought"
    events = db.events.select_events_by_character(chars[1]["id"])
    assert len(events) == 1
    assert events[0]["type"] == "thought"


def test_select_most_recent_event(chars: Tuple[db.Character, db.Character]) -> None:
    """
    Test the select_most_recent_event function.
    """
    assert chars[0]["id"]
    assert chars[1]["id"]
    event1 = db.Event(
        character=chars[0]["id"],
        type="event",
        content="test event",
    )
    event2 = db.Event(
        character=chars[1]["id"],
        type="thought",
        content="test thought",
    )
    event3 = db.Event(
        character=chars[0]["id"],
        type="thought",
        content="test thought 2",
    )
    db.events.insert_event(event1)
    time.sleep(1)
    event2_id = db.events.insert_event(event2)
    time.sleep(1)
    event3_id = db.events.insert_event(event3)
    event = db.events.select_most_recent_event(chars[0]["id"])
    assert event["id"] == event3_id
    assert event["type"] == "thought"
    event = db.events.select_most_recent_event(chars[1]["id"])
    assert event["id"] == event2_id
    assert event["type"] == "thought"


def test_delete_event(chars: Tuple[db.Character, db.Character]) -> None:
    """
    Test the delete_event function.
    """
    assert chars[0]["id"]
    event1 = db.Event(
        character=chars[0]["id"],
        type="event",
        content="test event",
    )
    event2 = db.Event(
        character=chars[0]["id"],
        type="thought",
        content="test thought",
    )
    event1_id = db.events.insert_event(event1)
    event2_id = db.events.insert_event(event2)
    db.events.delete_event(event1_id)
    events = db.events.select_events_by_character(chars[0]["id"])
    assert len(events) == 1
    assert events[0]["id"] == event2_id
