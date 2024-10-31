"""
This file contains the tests for the database/events.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

import time
from datetime import datetime, timezone
from typing import Generator

import pytest

import database_old as db
from not_t.test_database_old.test_characters import char_1, char_2
from not_t.test_database_old.test_main import db_init


@pytest.fixture
def event_1(char_1: db.Character) -> Generator[db.Event, None, None]:
    """
    Creates a event to be used in testing.
    """
    event = db.Event(
        char_id=char_1["id"],
        type="event",
        content="test event",
        timestamp=db.convert_dt_ts(datetime.now(timezone.utc)),
    )
    event["id"] = db.events.insert_event(event)
    yield event


@pytest.fixture
def event_2(char_1: db.Character) -> Generator[db.Event, None, None]:
    """
    Creates a event distinct from event_1 to be used in testing.
    """
    event = db.Event(
        char_id=char_1["id"],
        type="thought",
        content="test thought",
    )
    event["id"] = db.events.insert_event(event)
    yield event


def test_insert_event(db_init: str, char_1: db.Character, char_2: db.Character) -> None:
    """
    Test the insert_event function.
    """
    event1 = db.Event(
        char_id=char_1["id"],
        type="event",
        content="test event",
    )
    event2 = db.Event(
        char_id=char_2["id"],
        type="thought",
        content="test thought",
    )
    event1_id = db.events.insert_event(event1)
    event2_id = db.events.insert_event(event2)
    assert event1_id == 1
    assert event2_id == 2


def test_select_events(
    db_init: str, char_1: db.Character, char_2: db.Character
) -> None:
    """
    Test the select_events.
    """
    assert char_1["id"]
    assert char_2["id"]
    event1 = db.Event(
        char_id=char_1["id"],
        type="event",
        content="test event",
    )
    event2 = db.Event(
        char_id=char_2["id"],
        type="thought",
        content="test thought",
    )
    event3 = db.Event(
        char_id=char_1["id"],
        type="thought",
        content="test thought 2",
    )
    db.events.insert_event(event1)
    db.events.insert_event(event2)
    db.events.insert_event(event3)
    events = db.events.select_events()
    assert len(events) == 3
    assert events[0]["type"] == "event"
    assert events[1]["type"] == "thought"
    assert events[2]["type"] == "thought"


def test_select_events_with_query(
    db_init: str, char_1: db.Character, char_2: db.Character
) -> None:
    """
    Test the select_events with a query specifying a character.
    """
    assert char_1["id"]
    assert char_2["id"]
    event1 = db.Event(
        char_id=char_1["id"],
        type="event",
        content="test event",
    )
    event2 = db.Event(
        char_id=char_2["id"],
        type="thought",
        content="test thought",
    )
    event3 = db.Event(
        char_id=char_1["id"],
        type="thought",
        content="test thought 2",
    )
    db.events.insert_event(event1)
    db.events.insert_event(event2)
    db.events.insert_event(event3)
    events = db.events.select_events(db.Event(char_id=char_1["id"]))
    assert len(events) == 2
    assert events[0]["type"] == "event"
    assert events[1]["type"] == "thought"
    events = db.events.select_events(db.Event(char_id=char_2["id"]))
    assert len(events) == 1
    assert events[0]["type"] == "thought"


def test_select_most_recent_event(
    db_init: str, char_1: db.Character, char_2: db.Character
) -> None:
    """
    Test the select_most_recent_event function.
    """
    assert char_1["id"]
    assert char_2["id"]
    event1 = db.Event(
        char_id=char_1["id"],
        type="event",
        content="test event",
    )
    event2 = db.Event(
        char_id=char_2["id"],
        type="thought",
        content="test thought",
    )
    event3 = db.Event(
        char_id=char_1["id"],
        type="thought",
        content="test thought 2",
    )
    db.events.insert_event(event1)
    time.sleep(1)
    event2_id = db.events.insert_event(event2)
    time.sleep(1)
    event3_id = db.events.insert_event(event3)
    event = db.events.select_most_recent_event(char_1["id"])
    assert event["id"] == event3_id
    assert event["type"] == "thought"
    event = db.events.select_most_recent_event(char_2["id"])
    assert event["id"] == event2_id
    assert event["type"] == "thought"


def test_delete_event(db_init: str, char_1: db.Character) -> None:
    """
    Test the delete_event function.
    """
    assert char_1["id"]
    event1 = db.Event(
        char_id=char_1["id"],
        type="event",
        content="test event",
    )
    event2 = db.Event(
        char_id=char_1["id"],
        type="thought",
        content="test thought",
    )
    event1_id = db.events.insert_event(event1)
    event2_id = db.events.insert_event(event2)
    db.events.delete_event(event1_id)
    events = db.events.select_events(db.Event(char_id=char_1["id"]))
    assert len(events) == 1
    assert events[0]["id"] == event2_id
