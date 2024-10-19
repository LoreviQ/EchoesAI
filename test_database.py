"""
This file contains the tests for the database.py file.
"""

# pylint: disable=redefined-outer-name
import os
import time
from datetime import datetime, timedelta
from typing import Generator

import pytest

from database import DB


@pytest.fixture
def db() -> Generator[DB, None, None]:
    """
    Create a DB object for testing and teardown after testing.
    """
    test_name = os.environ.get("PYTEST_CURRENT_TEST")
    if test_name is None:
        test_name = "unknown"
    else:
        test_name = test_name.split(":")[-1].split(" ")[0]
    db_path = f"test_database_{test_name}.db"
    db = DB(db_path)
    yield db
    os.remove(db_path)


def test_create_database() -> None:
    """
    Test the creation of the database.
    """
    DB("test_database.db")
    assert os.path.exists("test_database.db")
    os.remove("test_database.db")


def test_post_thread(db: DB) -> None:
    """
    Test the post_thread method of the DB class.
    """
    thread_id = db.post_thread("user", "chatbot")
    assert thread_id == 1
    thread_id = db.post_thread("user2", "chatbot2")
    assert thread_id == 2


def test_get_thread(db: DB) -> None:
    """
    Test the get_thread method of the DB class.
    """
    thread_id = db.post_thread("user", "chatbot")
    user, chatbot, phase = db.get_thread(thread_id)
    assert user == "user"
    assert chatbot == "chatbot"
    assert phase == 0
    with pytest.raises(ValueError, match="Thread not found"):
        db.get_thread(2)


def test_get_threads_by_user(db: DB) -> None:
    """
    Test the get_threads_by_user method of the DB class.
    """
    db.post_thread("user", "chatbot")
    db.post_thread("user", "chatbot2")
    db.post_thread("user2", "chatbot")
    threads = db.get_threads_by_user("user")
    assert threads == [(1, "chatbot"), (2, "chatbot2")]
    threads = db.get_threads_by_user("user2")
    assert threads == [(3, "chatbot")]


def test_get_latest_thread(db: DB) -> None:
    """
    Test the get_latest_thread method of the DB class.
    """
    db.post_thread("user", "chatbot")
    thread_id = db.post_thread("user", "chatbot")
    latest_thread = db.get_latest_thread("user", "chatbot")
    assert latest_thread == thread_id
    latest_thread = db.get_latest_thread("user2", "chatbot2")
    assert latest_thread == 0


def test_post_message(db: DB) -> None:
    """
    Test the post_message method of the DB class.
    """
    thread_id = db.post_thread("user", "chatbot")
    db.post_message(thread_id, "test message", "user")


def test_get_messages(db: DB) -> None:
    """
    Test the get_messages method of the DB class.
    """
    thread_id = db.post_thread("user", "chatbot")
    thread_id2 = db.post_thread("user2", "chatbot2")
    db.post_message(thread_id, "test message", "user")
    db.post_message(thread_id2, "test message2", "assistant")
    messages = db.get_messages()
    assert len(messages) == 2
    assert messages[0][1] == "test message"
    assert messages[0][2] == "user"
    assert messages[1][1] == "test message2"
    assert messages[1][2] == "assistant"


def test_get_messages_by_thread(db: DB) -> None:
    """
    Test the get_messages_by_thread method of the DB class.
    """
    thread_id = db.post_thread("user", "chatbot")
    thread_id2 = db.post_thread("user2", "chatbot2")
    db.post_message(thread_id, "test message", "user")
    db.post_message(thread_id2, "test message2", "assistant")
    messages = db.get_messages_by_thread(thread_id)
    assert len(messages) == 1
    assert messages[0][1] == "test message"
    messages = db.get_messages_by_thread(thread_id2)
    assert len(messages) == 1
    assert messages[0][1] == "test message2"


def test_delete_messages_more_recent(db: DB) -> None:
    """
    Test the delete_messages_more_recent method of the DB class.
    """
    # Setup messages
    thread_id = db.post_thread("user", "chatbot")
    alt_thread = db.post_thread("user2", "chatbot2")
    db.post_message(thread_id, "test message", "user")
    time.sleep(1)  # Ensure the messages have different timestamps
    db.post_message(thread_id, "test message2", "assistant")
    time.sleep(1)
    db.post_message(thread_id, "test message3", "user")
    db.post_message(alt_thread, "alt message", "user")

    # Check that messages are deleted correctly
    db.delete_messages_more_recent(2)
    messages = db.get_messages_by_thread(thread_id)
    assert len(messages) == 1
    assert messages[0][1] == "test message"
    db.delete_messages_more_recent(1)
    messages = db.get_messages_by_thread(thread_id)
    assert len(messages) == 0

    # Check that messages from other threads are not deleted
    messages = db.get_messages_by_thread(alt_thread)
    assert len(messages) == 1
    assert messages[0][1] == "alt message"


def test_apply_scheduled_message(db: DB) -> None:
    """
    Test the apply_scheduled_message method of the DB class.
    """
    thread_id = db.post_thread("user", "chat")
    db.post_message(thread_id, "test message", "user")
    time.sleep(1)
    # false since there is no scheduled message
    valid = db.apply_scheduled_message(thread_id)
    assert not valid

    # true since there is a scheduled message
    db.post_message(
        thread_id, "test message2", "assistant", datetime.now() + timedelta(minutes=5)
    )
    valid = db.apply_scheduled_message(thread_id)
    assert valid

    # false since there are multiple scheduled messages
    db.post_message(
        thread_id, "test message3", "assistant", datetime.now() + timedelta(minutes=5)
    )
    db.post_message(
        thread_id, "test message4", "assistant", datetime.now() + timedelta(minutes=5)
    )
    valid = db.apply_scheduled_message(thread_id)
    assert not valid


def test_post_event(db: DB) -> None:
    """
    Test
    """
    event_id = db.post_event("chatbot", "event", "test event")
    assert event_id == 1


def test_get_events_by_type_and_chatbot(db: DB) -> None:
    """
    Test
    """
    db.post_event("chatbot", "event", "test event")
    db.post_event("chatbot", "event", "test event2")
    db.post_event("chatbot", "thought", "test event3")
    events = db.get_events_by_type_and_chatbot("event", "chatbot")
    assert len(events) == 2
    assert events[0][2] == "test event"
    assert events[1][2] == "test event2"
    events = db.get_events_by_type_and_chatbot("thought", "chatbot")
    assert len(events) == 1
    assert events[0][2] == "test event3"


def test_delete_event(db: DB) -> None:
    """
    Test
    """
    event_id = db.post_event("chatbot", "event", "test event")
    db.delete_event(event_id)
    events = db.get_events_by_type_and_chatbot("event", "chatbot")
    assert len(events) == 0
    with pytest.raises(ValueError, match="Event not found"):
        db.delete_event(2)
