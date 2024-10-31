"""Tests for the threads module in the database package."""

# pylint: disable=redefined-outer-name unused-argument unused-import


from datetime import datetime, timedelta, timezone

import pytest

import database as db

from .fixtures import character, characters, thread, user
from .test_main import test_db


def test_insert_message(thread: db.Thread) -> None:
    """Test the insert_message function."""
    message = db.Message(
        thread_id=thread["id"],
        content="test message",
        role="user",
    )
    result = db.insert_message(message)
    assert result == 1


def test_select_message(thread: db.Thread) -> None:
    """Test the select_message function."""
    message = db.Message(
        thread_id=thread["id"],
        content="test message",
        role="user",
    )
    message_id = db.insert_message(message)
    result = db.select_message(message_id)
    assert result["thread_id"] == thread["id"]
    assert result["content"] == "test message"
    assert result["role"] == "user"


def test_select_messages_without_query(thread: db.Thread) -> None:
    """Test the select messages function without a query."""
    message = db.Message(
        thread_id=thread["id"],
        content="test message",
        role="user",
    )
    message2 = db.Message(
        thread_id=thread["id"],
        content="test message 2",
        role="user",
    )
    db.insert_message(message)
    db.insert_message(message2)
    result = db.select_messages()
    assert len(result) == 2
    assert result[0]["thread_id"] == thread["id"]
    assert result[0]["content"] == "test message"
    assert result[0]["role"] == "user"
    assert result[1]["thread_id"] == thread["id"]
    assert result[1]["content"] == "test message 2"
    assert result[1]["role"] == "user"


def test_select_messages_with_query(thread: db.Thread) -> None:
    """Test the select messages function with a query."""
    message = db.Message(
        thread_id=thread["id"],
        content="test message",
        role="user",
    )
    message2 = db.Message(
        thread_id=thread["id"],
        content="test message 2",
        role="user",
    )
    message3 = db.Message(
        thread_id=thread["id"],
        content="test message 3",
        role="assistant",
    )
    db.insert_message(message)
    db.insert_message(message2)
    db.insert_message(message3)
    query = db.Message(role="user")
    result = db.select_messages(query)
    assert len(result) == 2
    assert result[0]["content"] == "test message"
    assert result[1]["content"] == "test message 2"


def test_select_scheduled_message(thread: db.Thread) -> None:
    """Test the select_scheduled_message function."""
    now = datetime.now(timezone.utc)
    message = db.Message(
        thread_id=thread["id"],
        content="test message",
        role="user",
    )
    message2 = db.Message(
        thread_id=thread["id"],
        content="test message 2",
        role="user",
        timestamp=now + timedelta(days=1),
    )
    db.insert_message(message)
    db.insert_message(message2)
    result = db.select_scheduled_message(thread["id"])
    assert result["content"] == "test message 2"


def test_select_scheduled_message_none_scheduled(thread: db.Thread) -> None:
    """Test the select_scheduled_message function when no messages are scheduled."""
    message = db.Message(
        thread_id=thread["id"],
        content="test message",
        role="user",
    )
    db.insert_message(message)
    with pytest.raises(ValueError):
        db.select_scheduled_message(thread["id"])


def test_delete_message(thread: db.Thread) -> None:
    """Test the delete_message function."""
    message = db.Message(
        thread_id=thread["id"],
        content="test message",
        role="user",
    )
    message_id = db.insert_message(message)
    db.delete_message(message_id)
    messages = db.select_messages()
    assert len(messages) == 0


def test_delete_messages_more_recent(thread: db.Thread) -> None:
    """Test the delete_messages_more_recent function."""
    now = datetime.now(timezone.utc)
    message = db.Message(
        thread_id=thread["id"],
        content="test message",
        role="user",
    )
    message2 = db.Message(
        thread_id=thread["id"],
        content="test message 2",
        role="user",
        timestamp=now + timedelta(days=1),
    )
    message3 = db.Message(
        thread_id=thread["id"],
        content="test message 3",
        role="assistant",
        timestamp=now + timedelta(days=2),
    )
    message_id = db.insert_message(message)
    message2_id = db.insert_message(message2)
    db.insert_message(message3)
    db.delete_messages_more_recent(message2_id)
    messages = db.select_messages()
    assert len(messages) == 1
    assert messages[0]["id"] == message_id


def test_delete_scheduled_messages(thread: db.Thread) -> None:
    """Test the delete_scheduled_messages function."""
    now = datetime.now(timezone.utc)
    message = db.Message(
        thread_id=thread["id"],
        content="test message",
        role="user",
    )
    message2 = db.Message(
        thread_id=thread["id"],
        content="test message 2",
        role="user",
        timestamp=now + timedelta(days=1),
    )
    message3 = db.Message(
        thread_id=thread["id"],
        content="test message 3",
        role="assistant",
        timestamp=now + timedelta(days=2),
    )
    message_id = db.insert_message(message)
    db.insert_message(message2)
    db.insert_message(message3)
    db.delete_scheduled_messages(thread["id"])
    messages = db.select_messages()
    assert len(messages) == 1
    assert messages[0]["id"] == message_id


def test_update_message(thread: db.Thread) -> None:
    """Test the update_message function."""
    message = db.Message(
        thread_id=thread["id"],
        content="test message",
        role="user",
    )
    message_id = db.insert_message(message)
    message = db.select_message(message_id)
    message["content"] = "updated message"
    db.update_message(message)
    result = db.select_message(message_id)
    assert result["content"] == "updated message"
