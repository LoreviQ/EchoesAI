"""
This file contains the tests for the database/dbpy file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

import os
import time
from datetime import datetime, timedelta
from typing import Tuple

import database as db
from tests.test_database.test_characters import char_1, char_2
from tests.test_database.test_main import db_init
from tests.test_database.test_threads import thread_1, thread_2


def test_insert_message(db_init: str, thread_1: db.Thread) -> None:
    """
    Test the insert_message function.
    """
    message = db.Message(thread=thread_1, content="test message", role="user")
    message_id = db.insert_message(message)
    assert message_id == 1
    message = db.Message(
        timestamp=datetime.now() + timedelta(days=1),
        thread=thread_1,
        content="test message 2",
        role="assistant",
    )
    message_id = db.insert_message(message)
    assert message_id == 2


def test_select_messages_by_thread(
    db_init: str, thread_1: db.Thread, thread_2: db.Thread
) -> None:
    """
    Test the select_messages_by_thread function.
    """
    assert thread_1["id"]
    assert thread_2["id"]
    message1 = db.Message(thread=thread_1, content="test message", role="user")
    message2 = db.Message(thread=thread_1, content="test message 2", role="assistant")
    message3 = db.Message(thread=thread_2, content="test message 3", role="user")
    message1_id = db.insert_message(message1)
    message2_id = db.insert_message(message2)
    message3_id = db.insert_message(message3)
    messages = db.select_messages_by_thread(thread_1["id"])
    assert len(messages) == 2
    assert messages[0]["id"] == message1_id
    assert messages[0]["content"] == "test message"
    assert messages[1]["id"] == message2_id
    assert messages[1]["content"] == "test message 2"
    messages = db.select_messages_by_thread(thread_2["id"])
    assert len(messages) == 1
    assert messages[0]["id"] == message3_id
    assert messages[0]["content"] == "test message 3"


def test_select_messages_by_character(
    db_init: str, thread_1: db.Thread, thread_2: db.Thread
) -> None:
    """
    Test the select_messages_by_character function.
    """
    assert thread_1["character"]
    assert thread_2["character"]
    message1 = db.Message(thread=thread_1, content="test message", role="user")
    message2 = db.Message(thread=thread_1, content="test message 2", role="assistant")
    message3 = db.Message(thread=thread_2, content="test message 3", role="user")
    message1_id = db.insert_message(message1)
    message2_id = db.insert_message(message2)
    message3_id = db.insert_message(message3)
    messages = db.select_messages_by_character(thread_1["character"])
    assert len(messages) == 2
    assert messages[0]["id"] == message1_id
    assert messages[0]["content"] == "test message"
    assert messages[1]["id"] == message2_id
    assert messages[1]["content"] == "test message 2"
    messages = db.select_messages_by_character(thread_2["character"])
    assert len(messages) == 1
    assert messages[0]["id"] == message3_id
    assert messages[0]["content"] == "test message 3"


def test_delete_messages_more_recent(
    db_init: str, thread_1: db.Thread, thread_2: db.Thread
) -> None:
    """
    Test the delete_messages_more_recent function.
    """
    assert thread_1["id"]
    assert thread_2["id"]
    message1 = db.Message(thread=thread_1, content="test message", role="user")
    message2 = db.Message(thread=thread_1, content="test message 2", role="assistant")
    message3 = db.Message(thread=thread_1, content="test message 3", role="user")
    message4 = db.Message(thread=thread_2, content="test message 4", role="user")
    message1_id = db.insert_message(message1)
    time.sleep(1)
    message2_id = db.insert_message(message2)
    time.sleep(1)
    db.insert_message(message3)
    time.sleep(1)
    message4_id = db.insert_message(message4)
    db.delete_messages_more_recent(message2_id)
    messages = db.select_messages_by_thread(thread_1["id"])
    assert len(messages) == 1
    assert messages[0]["id"] == message1_id
    messages = db.select_messages_by_thread(thread_2["id"])
    assert len(messages) == 1
    assert messages[0]["id"] == message4_id


def test_delete_scheduled_messages_from_thread(
    db_init: str, thread_1: db.Thread, thread_2: db.Thread
) -> None:
    """
    Test the delete_scheduled_messages_from_thread function.
    """
    assert thread_1["id"]
    assert thread_2["id"]
    message1 = db.Message(thread=thread_1, content="test message", role="user")
    message2 = db.Message(thread=thread_1, content="test message 2", role="assistant")
    message3 = db.Message(
        thread=thread_1,
        content="test message 3",
        role="user",
        timestamp=datetime.now() + timedelta(days=1),
    )
    message4 = db.Message(thread=thread_2, content="test message 4", role="user")
    message1_id = db.insert_message(message1)
    message2_id = db.insert_message(message2)
    db.insert_message(message3)
    message4_id = db.insert_message(message4)
    db.delete_scheduled_messages_from_thread(thread_1["id"])
    messages = db.select_messages_by_thread(thread_1["id"])
    assert len(messages) == 2
    assert messages[0]["id"] == message1_id
    assert messages[1]["id"] == message2_id
    messages = db.select_messages_by_thread(thread_2["id"])
    assert len(messages) == 1
    assert messages[0]["id"] == message4_id


def test_select_scheduled_message_id(
    db_init: str, thread_1: db.Thread, thread_2: db.Thread
) -> None:
    """
    Test the select_scheduled_message_id function.
    """
    assert thread_1["id"]
    message1 = db.Message(thread=thread_1, content="test message", role="user")
    message2 = db.Message(
        thread=thread_1,
        content="test message 2",
        role="assistant",
        timestamp=datetime.now() + timedelta(days=1),
    )
    message3 = db.Message(thread=thread_2, content="test message 3", role="user")
    db.insert_message(message1)
    message2_id = db.insert_message(message2)
    db.insert_message(message3)
    message_id = db.select_scheduled_message_id(thread_1["id"])
    assert message_id == message2_id


def test_update_message(db_init: str, thread_1: db.Thread, thread_2: db.Thread) -> None:
    """
    Test the update_message function.
    """
    assert thread_1["id"]
    assert thread_2["id"]
    message1 = db.Message(thread=thread_1, content="test message", role="user")
    message2 = db.Message(
        thread=thread_1,
        content="test message 2",
        role="assistant",
        timestamp=datetime.now() + timedelta(days=1),
    )
    message3 = db.Message(thread=thread_2, content="test message 3", role="user")
    message1_id = db.insert_message(message1)
    message2_id = db.insert_message(message2)
    message3_id = db.insert_message(message3)
    message_patch = db.Message(
        id=message2_id,
        content="test message patched",
        timestamp=datetime.now(),
    )
    db.update_message(message_patch)
    messages = db.select_messages_by_thread(thread_1["id"])
    assert len(messages) == 2
    assert messages[0]["id"] == message1_id
    assert messages[0]["content"] == "test message"
    assert messages[1]["id"] == message2_id
    assert messages[1]["content"] == "test message patched"
    messages = db.select_messages_by_thread(thread_2["id"])
    assert len(messages) == 1
    assert messages[0]["id"] == message3_id
    assert messages[0]["content"] == "test message 3"
