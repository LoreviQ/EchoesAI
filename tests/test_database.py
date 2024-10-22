"""
This file contains the tests for the database.py file.
"""

# pylint: disable=redefined-outer-name
import os
import time
from datetime import datetime, timedelta, timezone
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
    thread = db.get_thread(thread_id)
    assert thread["user"] == "user"
    assert thread["chatbot"] == "chatbot"
    assert thread["phase"] == 0
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
    assert threads == [
        {"id": 1, "user": "user", "chatbot": "chatbot", "phase": 0},
        {"id": 2, "user": "user", "chatbot": "chatbot2", "phase": 0},
    ]
    threads = db.get_threads_by_user("user2")
    assert threads == [{"id": 3, "user": "user2", "chatbot": "chatbot", "phase": 0}]


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
    assert messages[0]["content"] == "test message"
    assert messages[0]["role"] == "user"
    assert messages[1]["content"] == "test message2"
    assert messages[1]["role"] == "assistant"


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
    assert messages[0]["content"] == "test message"
    messages = db.get_messages_by_thread(thread_id2)
    assert len(messages) == 1
    assert messages[0]["content"] == "test message2"


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
    assert messages[0]["content"] == "test message"
    db.delete_messages_more_recent(1)
    messages = db.get_messages_by_thread(thread_id)
    assert len(messages) == 0

    # Check that messages from other threads are not deleted
    messages = db.get_messages_by_thread(alt_thread)
    assert len(messages) == 1
    assert messages[0]["content"] == "alt message"


def test_delete_scheduled_messages_from_thread(db: DB) -> None:
    """
    Test the delete_scheduled_messages_from_thread method of the DB class.
    """
    thread_id = db.post_thread("user", "chatbot")
    db.post_message(thread_id, "test message", "user")
    db.post_message(
        thread_id,
        "test message2",
        "assistant",
        datetime.now(timezone.utc) + timedelta(days=1),
    )
    db.delete_scheduled_messages_from_thread(thread_id)
    messages = db.get_messages_by_thread(thread_id)
    assert len(messages) == 1


def get_scheduled_message(db: DB) -> None:
    """
    Test the get_scheduled_message method of the DB class.
    """
    thread_id = db.post_thread("user", "chatbot")
    db.post_message(thread_id, "test message", "user")
    db.post_message(
        thread_id,
        "test message2",
        "assistant",
        datetime.now(timezone.utc) + timedelta(days=1),
    )
    message_id = db.get_scheduled_message(thread_id)
    assert message_id == 2


def test_update_message(db: DB) -> None:
    """
    Test the update_message method of the DB class.
    """
    thread_id = db.post_thread("user", "chatbot")
    db.post_message(thread_id, "test message", "user")
    db.post_message(
        thread_id,
        "test message2",
        "assistant",
        datetime.now(timezone.utc) + timedelta(days=1),
    )
    db.update_message(
        2, datetime.now(timezone.utc) - timedelta(days=1), "test message3"
    )
    messages = db.get_messages_by_thread(thread_id)
    assert messages[1]["content"] == "test message3"
    assert messages[1]["timestamp"] < datetime.now(timezone.utc)


def test_post_event(db: DB) -> None:
    """
    Test
    """
    event_id = db.post_event("chatbot", "event", "test event")
    assert event_id == 1


def test_get_events_by_chatbot(db: DB) -> None:
    """
    Test
    """
    db.post_event("chatbot", "event", "test event")
    db.post_event("chatbot", "event", "test event2")
    db.post_event("chatbot", "thought", "test event3")
    events = db.get_events_by_chatbot("chatbot")
    assert len(events) == 3
    assert events[0]["content"] == "test event"
    assert events[0]["type"] == "event"
    assert events[1]["content"] == "test event2"
    assert events[1]["type"] == "event"
    assert events[2]["content"] == "test event3"
    assert events[2]["type"] == "thought"


def test_delete_event(db: DB) -> None:
    """
    Test
    """
    event_id = db.post_event("chatbot", "event", "test event")
    db.delete_event(event_id)
    events = db.get_events_by_chatbot("chatbot")
    assert len(events) == 0
    with pytest.raises(ValueError, match="Event not found"):
        db.delete_event(2)


def test_post_social_media_post(db: DB) -> None:
    """
    Test
    """
    db.post_social_media_post("chatbot", "test post", "test,prompt,", "test caption")


def test_get_posts_by_character(db: DB) -> None:
    """
    Test
    """
    db.post_social_media_post("chatbot", "test post", "test,prompt,", "test caption")
    db.post_social_media_post("chatbot", "test post2", "test,prompt,", "test caption2")
    db.post_social_media_post("chatbot", "test post3", "test,prompt,", "test caption3")
    db.post_social_media_post("chatbot2", "test post", "test,prompt,", "test caption")
    posts = db.get_posts_by_character("chatbot")
    assert len(posts) == 3
    assert posts[0]["description"] == "test post"
    assert posts[1]["description"] == "test post2"
    assert posts[2]["description"] == "test post3"
