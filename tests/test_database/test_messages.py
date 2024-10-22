"""
This file contains the tests for the database/messages.py file.
"""

import os
import time
from datetime import datetime, timedelta
from typing import Generator

import pytest

import database as db

# pylint: disable=redefined-outer-name unused-argument unused-import


@pytest.fixture
def threads(monkeypatch) -> Generator[str, None, None]:
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
    db.main.create_db()
    character_1 = db.characters.Character(name="test character")
    character_1["id"] = db.characters.insert_character(character_1)
    character_2 = db.characters.Character(name="test character 2")
    character_2["id"] = db.characters.insert_character(character_2)
    thread_id_1 = db.threads.insert_thread("user", character_1["id"])
    thread_id_2 = db.threads.insert_thread("user2", character_2["id"])
    thread1 = db.threads.select_thread(thread_id_1)
    thread2 = db.threads.select_thread(thread_id_2)
    yield thread1, thread2
    os.remove(db_path)


def test_insert_message(threads) -> None:
    """
    Test the insert_message function.
    """
    message = db.messages.Message(
        thread=threads[0], content="test message", role="user"
    )
    message_id = db.messages.insert_message(message)
    assert message_id == 1
    message = db.messages.Message(
        timestamp=datetime.now() + timedelta(days=1),
        thread=threads[0],
        content="test message 2",
        role="assistant",
    )
    message_id = db.messages.insert_message(message)
    assert message_id == 2


def test_select_messages_by_thread(threads) -> None:
    """
    Test the select_messages_by_thread function.
    """
    message1 = db.messages.Message(
        thread=threads[0], content="test message", role="user"
    )
    message2 = db.messages.Message(
        thread=threads[0], content="test message 2", role="assistant"
    )
    message3 = db.messages.Message(
        thread=threads[1], content="test message 3", role="user"
    )
    message1_id = db.messages.insert_message(message1)
    message2_id = db.messages.insert_message(message2)
    message3_id = db.messages.insert_message(message3)
    messages = db.messages.select_messages_by_thread(threads[0]["id"])
    assert len(messages) == 2
    assert messages[0]["id"] == message1_id
    assert messages[0]["content"] == "test message"
    assert messages[1]["id"] == message2_id
    assert messages[1]["content"] == "test message 2"
    messages = db.messages.select_messages_by_thread(threads[1]["id"])
    assert len(messages) == 1
    assert messages[0]["id"] == message3_id
    assert messages[0]["content"] == "test message 3"


def test_select_messages_by_character(threads) -> None:
    """
    Test the select_messages_by_character function.
    """
    message1 = db.messages.Message(
        thread=threads[0], content="test message", role="user"
    )
    message2 = db.messages.Message(
        thread=threads[0], content="test message 2", role="assistant"
    )
    message3 = db.messages.Message(
        thread=threads[1], content="test message 3", role="user"
    )
    message1_id = db.messages.insert_message(message1)
    message2_id = db.messages.insert_message(message2)
    message3_id = db.messages.insert_message(message3)
    messages = db.messages.select_messages_by_character(threads[0]["character"])
    assert len(messages) == 2
    assert messages[0]["id"] == message1_id
    assert messages[0]["content"] == "test message"
    assert messages[1]["id"] == message2_id
    assert messages[1]["content"] == "test message 2"
    messages = db.messages.select_messages_by_character(threads[1]["character"])
    assert len(messages) == 1
    assert messages[0]["id"] == message3_id
    assert messages[0]["content"] == "test message 3"


def test_delete_messages_more_recent(threads) -> None:
    """
    Test the delete_messages_more_recent function.
    """
    message1 = db.messages.Message(
        thread=threads[0], content="test message", role="user"
    )
    message2 = db.messages.Message(
        thread=threads[0], content="test message 2", role="assistant"
    )
    message3 = db.messages.Message(
        thread=threads[0], content="test message 3", role="user"
    )
    message4 = db.messages.Message(
        thread=threads[1], content="test message 4", role="user"
    )
    message1_id = db.messages.insert_message(message1)
    time.sleep(1)
    message2_id = db.messages.insert_message(message2)
    time.sleep(1)
    db.messages.insert_message(message3)
    time.sleep(1)
    message4_id = db.messages.insert_message(message4)
    db.messages.delete_messages_more_recent(message2_id)
    messages = db.messages.select_messages_by_thread(threads[0]["id"])
    assert len(messages) == 1
    assert messages[0]["id"] == message1_id
    messages = db.messages.select_messages_by_thread(threads[1]["id"])
    assert len(messages) == 1
    assert messages[0]["id"] == message4_id


def test_delete_scheduled_messages_from_thread(threads) -> None:
    """
    Test the delete_scheduled_messages_from_thread function.
    """
    message1 = db.messages.Message(
        thread=threads[0], content="test message", role="user"
    )
    message2 = db.messages.Message(
        thread=threads[0], content="test message 2", role="assistant"
    )
    message3 = db.messages.Message(
        thread=threads[0],
        content="test message 3",
        role="user",
        timestamp=datetime.now() + timedelta(days=1),
    )
    message4 = db.messages.Message(
        thread=threads[1], content="test message 4", role="user"
    )
    message1_id = db.messages.insert_message(message1)
    message2_id = db.messages.insert_message(message2)
    db.messages.insert_message(message3)
    message4_id = db.messages.insert_message(message4)
    db.messages.delete_scheduled_messages_from_thread(threads[0]["id"])
    messages = db.messages.select_messages_by_thread(threads[0]["id"])
    assert len(messages) == 2
    assert messages[0]["id"] == message1_id
    assert messages[1]["id"] == message2_id
    messages = db.messages.select_messages_by_thread(threads[1]["id"])
    assert len(messages) == 1
    assert messages[0]["id"] == message4_id


def test_select_scheduled_message_id(threads) -> None:
    """
    Test the select_scheduled_message_id function.
    """
    message1 = db.messages.Message(
        thread=threads[0], content="test message", role="user"
    )
    message2 = db.messages.Message(
        thread=threads[0],
        content="test message 2",
        role="assistant",
        timestamp=datetime.now() + timedelta(days=1),
    )
    message3 = db.messages.Message(
        thread=threads[1], content="test message 3", role="user"
    )
    db.messages.insert_message(message1)
    message2_id = db.messages.insert_message(message2)
    db.messages.insert_message(message3)
    message_id = db.messages.select_scheduled_message_id(threads[0]["id"])
    assert message_id == message2_id


def test_update_message(threads) -> None:
    """
    Test the update_message function.
    """
    message1 = db.messages.Message(
        thread=threads[0], content="test message", role="user"
    )
    message2 = db.messages.Message(
        thread=threads[0],
        content="test message 2",
        role="assistant",
        timestamp=datetime.now() + timedelta(days=1),
    )
    message3 = db.messages.Message(
        thread=threads[1], content="test message 3", role="user"
    )
    message1_id = db.messages.insert_message(message1)
    message2_id = db.messages.insert_message(message2)
    message3_id = db.messages.insert_message(message3)
    message_patch = db.messages.Message(
        id=message2_id,
        content="test message patched",
        timestamp=datetime.now(),
    )
    db.messages.update_message(message_patch)
    messages = db.messages.select_messages_by_thread(threads[0]["id"])
    assert len(messages) == 2
    assert messages[0]["id"] == message1_id
    assert messages[0]["content"] == "test message"
    assert messages[1]["id"] == message2_id
    assert messages[1]["content"] == "test message patched"
    messages = db.messages.select_messages_by_thread(threads[1]["id"])
    assert len(messages) == 1
    assert messages[0]["id"] == message3_id
    assert messages[0]["content"] == "test message 3"
