"""
This file contains the tests for the database/threads.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

import time

import database as db
from tests.test_database.test_characters import char_1, char_2
from tests.test_database.test_main import db_init


def test_insert_event(db_init: str, char_1: db.Character, char_2: db.Character) -> None:
    """
    Test the insert_event function.
    """
    event1 = db.Event(
        character=char_1["id"],
        type="event",
        content="test event",
    )
    event2 = db.Event(
        character=char_2["id"],
        type="thought",
        content="test thought",
    )
    event1_id = db.events.insert_event(event1)
    event2_id = db.events.insert_event(event2)
    assert event1_id == 1
    assert event2_id == 2


def test_select_events_by_character(
    db_init: str, char_1: db.Character, char_2: db.Character
) -> None:
    """
    Test the select_events_by_character function.
    """
    assert char_1["id"]
    assert char_2["id"]
    event1 = db.Event(
        character=char_1["id"],
        type="event",
        content="test event",
    )
    event2 = db.Event(
        character=char_2["id"],
        type="thought",
        content="test thought",
    )
    event3 = db.Event(
        character=char_1["id"],
        type="thought",
        content="test thought 2",
    )
    db.events.insert_event(event1)
    db.events.insert_event(event2)
    db.events.insert_event(event3)
    events = db.events.select_events_by_character(char_1["id"])
    assert len(events) == 2
    assert events[0]["type"] == "event"
    assert events[1]["type"] == "thought"
    events = db.events.select_events_by_character(char_2["id"])
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
        character=char_1["id"],
        type="event",
        content="test event",
    )
    event2 = db.Event(
        character=char_2["id"],
        type="thought",
        content="test thought",
    )
    event3 = db.Event(
        character=char_1["id"],
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
        character=char_1["id"],
        type="event",
        content="test event",
    )
    event2 = db.Event(
        character=char_1["id"],
        type="thought",
        content="test thought",
    )
    event1_id = db.events.insert_event(event1)
    event2_id = db.events.insert_event(event2)
    db.events.delete_event(event1_id)
    events = db.events.select_events_by_character(char_1["id"])
    assert len(events) == 1
    assert events[0]["id"] == event2_id
