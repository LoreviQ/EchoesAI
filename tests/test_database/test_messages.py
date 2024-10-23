"""
This file contains the tests for the database/dbpy file.
"""

import os
import time
from datetime import datetime, timedelta
from typing import Generator, Tuple

import pytest

import database as db

# pylint: disable=redefined-outer-name unused-argument unused-import


@pytest.fixture
def threads(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[Tuple[db.Thread, db.Thread], None, None]:
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
    assert character_1["id"]
    assert character_2["id"]
    thread_id_1 = db.insert_thread("user", character_1["id"])
    thread_id_2 = db.insert_thread("user2", character_2["id"])
    thread1 = db.select_thread(thread_id_1)
    thread2 = db.select_thread(thread_id_2)
    yield thread1, thread2
    os.remove(db_path)


def test_insert_message(threads: Tuple[db.Thread, db.Thread]) -> None:
    """
    Test the insert_message function.
    """
    message = db.Message(thread=threads[0], content="test message", role="user")
    message_id = db.insert_message(message)
    assert message_id == 1
    message = db.Message(
        timestamp=datetime.now() + timedelta(days=1),
        thread=threads[0],
        content="test message 2",
        role="assistant",
    )
    message_id = db.insert_message(message)
    assert message_id == 2


def test_select_messages_by_thread(threads: Tuple[db.Thread, db.Thread]) -> None:
    """
    Test the select_messages_by_thread function.
    """
    assert threads[0]["id"]
    assert threads[1]["id"]
    message1 = db.Message(thread=threads[0], content="test message", role="user")
    message2 = db.Message(thread=threads[0], content="test message 2", role="assistant")
    message3 = db.Message(thread=threads[1], content="test message 3", role="user")
    message1_id = db.insert_message(message1)
    message2_id = db.insert_message(message2)
    message3_id = db.insert_message(message3)
    messages = db.select_messages_by_thread(threads[0]["id"])
    assert len(messages) == 2
    assert messages[0]["id"] == message1_id
    assert messages[0]["content"] == "test message"
    assert messages[1]["id"] == message2_id
    assert messages[1]["content"] == "test message 2"
    messages = db.select_messages_by_thread(threads[1]["id"])
    assert len(messages) == 1
    assert messages[0]["id"] == message3_id
    assert messages[0]["content"] == "test message 3"


def test_select_messages_by_character(threads: Tuple[db.Thread, db.Thread]) -> None:
    """
    Test the select_messages_by_character function.
    """
    assert threads[0]["character"]
    assert threads[1]["character"]
    message1 = db.Message(thread=threads[0], content="test message", role="user")
    message2 = db.Message(thread=threads[0], content="test message 2", role="assistant")
    message3 = db.Message(thread=threads[1], content="test message 3", role="user")
    message1_id = db.insert_message(message1)
    message2_id = db.insert_message(message2)
    message3_id = db.insert_message(message3)
    messages = db.select_messages_by_character(threads[0]["character"])
    assert len(messages) == 2
    assert messages[0]["id"] == message1_id
    assert messages[0]["content"] == "test message"
    assert messages[1]["id"] == message2_id
    assert messages[1]["content"] == "test message 2"
    messages = db.select_messages_by_character(threads[1]["character"])
    assert len(messages) == 1
    assert messages[0]["id"] == message3_id
    assert messages[0]["content"] == "test message 3"


def test_delete_messages_more_recent(threads: Tuple[db.Thread, db.Thread]) -> None:
    """
    Test the delete_messages_more_recent function.
    """
    assert threads[0]["id"]
    assert threads[1]["id"]
    message1 = db.Message(thread=threads[0], content="test message", role="user")
    message2 = db.Message(thread=threads[0], content="test message 2", role="assistant")
    message3 = db.Message(thread=threads[0], content="test message 3", role="user")
    message4 = db.Message(thread=threads[1], content="test message 4", role="user")
    message1_id = db.insert_message(message1)
    time.sleep(1)
    message2_id = db.insert_message(message2)
    time.sleep(1)
    db.insert_message(message3)
    time.sleep(1)
    message4_id = db.insert_message(message4)
    db.delete_messages_more_recent(message2_id)
    messages = db.select_messages_by_thread(threads[0]["id"])
    assert len(messages) == 1
    assert messages[0]["id"] == message1_id
    messages = db.select_messages_by_thread(threads[1]["id"])
    assert len(messages) == 1
    assert messages[0]["id"] == message4_id


def test_delete_scheduled_messages_from_thread(
    threads: Tuple[db.Thread, db.Thread]
) -> None:
    """
    Test the delete_scheduled_messages_from_thread function.
    """
    assert threads[0]["id"]
    assert threads[1]["id"]
    message1 = db.Message(thread=threads[0], content="test message", role="user")
    message2 = db.Message(thread=threads[0], content="test message 2", role="assistant")
    message3 = db.Message(
        thread=threads[0],
        content="test message 3",
        role="user",
        timestamp=datetime.now() + timedelta(days=1),
    )
    message4 = db.Message(thread=threads[1], content="test message 4", role="user")
    message1_id = db.insert_message(message1)
    message2_id = db.insert_message(message2)
    db.insert_message(message3)
    message4_id = db.insert_message(message4)
    db.delete_scheduled_messages_from_thread(threads[0]["id"])
    messages = db.select_messages_by_thread(threads[0]["id"])
    assert len(messages) == 2
    assert messages[0]["id"] == message1_id
    assert messages[1]["id"] == message2_id
    messages = db.select_messages_by_thread(threads[1]["id"])
    assert len(messages) == 1
    assert messages[0]["id"] == message4_id


def test_select_scheduled_message_id(threads: Tuple[db.Thread, db.Thread]) -> None:
    """
    Test the select_scheduled_message_id function.
    """
    assert threads[0]["id"]
    message1 = db.Message(thread=threads[0], content="test message", role="user")
    message2 = db.Message(
        thread=threads[0],
        content="test message 2",
        role="assistant",
        timestamp=datetime.now() + timedelta(days=1),
    )
    message3 = db.Message(thread=threads[1], content="test message 3", role="user")
    db.insert_message(message1)
    message2_id = db.insert_message(message2)
    db.insert_message(message3)
    message_id = db.select_scheduled_message_id(threads[0]["id"])
    assert message_id == message2_id


def test_update_message(threads: Tuple[db.Thread, db.Thread]) -> None:
    """
    Test the update_message function.
    """
    assert threads[0]["id"]
    assert threads[1]["id"]
    message1 = db.Message(thread=threads[0], content="test message", role="user")
    message2 = db.Message(
        thread=threads[0],
        content="test message 2",
        role="assistant",
        timestamp=datetime.now() + timedelta(days=1),
    )
    message3 = db.Message(thread=threads[1], content="test message 3", role="user")
    message1_id = db.insert_message(message1)
    message2_id = db.insert_message(message2)
    message3_id = db.insert_message(message3)
    message_patch = db.Message(
        id=message2_id,
        content="test message patched",
        timestamp=datetime.now(),
    )
    db.update_message(message_patch)
    messages = db.select_messages_by_thread(threads[0]["id"])
    assert len(messages) == 2
    assert messages[0]["id"] == message1_id
    assert messages[0]["content"] == "test message"
    assert messages[1]["id"] == message2_id
    assert messages[1]["content"] == "test message patched"
    messages = db.select_messages_by_thread(threads[1]["id"])
    assert len(messages) == 1
    assert messages[0]["id"] == message3_id
    assert messages[0]["content"] == "test message 3"
