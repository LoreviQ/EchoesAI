"""
This file contains the tests for the database/dbpy file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

import time
from datetime import datetime, timedelta, timezone
from typing import Generator

import pytest

import database as db
from tests.test_database.test_characters import char_1, char_2
from tests.test_database.test_main import db_init
from tests.test_database.test_threads import thread_1, thread_2
from tests.test_database.test_users import user_1, user_2


@pytest.fixture
def message_1(thread_1: db.Thread) -> Generator[db.Message, None, None]:
    """
    Creates a message to be used in testing.
    """
    message = db.Message(
        thread_id=thread_1,
        content="test message",
        role="user",
        timestamp=db.convert_dt_ts(datetime.now(timezone.utc) - timedelta(hours=1)),
    )
    message_id = db.insert_message(message)
    yield db.select_message(message_id)


@pytest.fixture
def message_2(thread_1: db.Thread) -> Generator[db.Message, None, None]:
    """
    Creates a message distinct from message_1 to be used in testing.
    """
    message = db.Message(thread_id=thread_1, content="test response", role="assistant")
    message_id = db.insert_message(message)
    yield db.select_message(message_id)


@pytest.fixture
def scheduled_message(thread_1: db.Thread) -> Generator[db.Message, None, None]:
    """
    Creates a message scheduled for the future to be used in testing.
    """
    message = db.Message(
        thread_id=thread_1,
        content="delayed response",
        role="assistant",
        timestamp=db.convert_dt_ts(datetime.now(timezone.utc) + timedelta(days=1)),
    )
    message_id = db.insert_message(message)
    yield db.select_message(message_id)


def test_insert_message(db_init: str, thread_1: db.Thread) -> None:
    """
    Test the insert_message function.
    """
    message = db.Message(thread_id=thread_1, content="test message", role="user")
    message_id = db.insert_message(message)
    assert message_id == 1
    message = db.Message(
        timestamp=db.convert_dt_ts(datetime.now() + timedelta(days=1)),
        thread_id=thread_1,
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
    message1 = db.Message(thread_id=thread_1, content="test message", role="user")
    message2 = db.Message(
        thread_id=thread_1, content="test message 2", role="assistant"
    )
    message3 = db.Message(thread_id=thread_2, content="test message 3", role="user")
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
    assert thread_1["char_id"]
    assert thread_2["char_id"]
    message1 = db.Message(thread_id=thread_1, content="test message", role="user")
    message2 = db.Message(
        thread_id=thread_1, content="test message 2", role="assistant"
    )
    message3 = db.Message(thread_id=thread_2, content="test message 3", role="user")
    message1_id = db.insert_message(message1)
    message2_id = db.insert_message(message2)
    message3_id = db.insert_message(message3)
    messages = db.select_messages_by_character(thread_1["char_id"])
    assert len(messages) == 2
    assert messages[0]["id"] == message1_id
    assert messages[0]["content"] == "test message"
    assert messages[1]["id"] == message2_id
    assert messages[1]["content"] == "test message 2"
    messages = db.select_messages_by_character(thread_2["char_id"])
    assert len(messages) == 1
    assert messages[0]["id"] == message3_id
    assert messages[0]["content"] == "test message 3"


def test_delete_messages_more_recent_db(
    db_init: str, thread_1: db.Thread, thread_2: db.Thread
) -> None:
    """
    Test the delete_messages_more_recent function.
    """
    assert thread_1["id"]
    assert thread_2["id"]
    message1 = db.Message(thread_id=thread_1, content="test message", role="user")
    message2 = db.Message(
        thread_id=thread_1, content="test message 2", role="assistant"
    )
    message3 = db.Message(thread_id=thread_1, content="test message 3", role="user")
    message4 = db.Message(thread_id=thread_2, content="test message 4", role="user")
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
    message1 = db.Message(thread_id=thread_1, content="test message", role="user")
    message2 = db.Message(
        thread_id=thread_1, content="test message 2", role="assistant"
    )
    message3 = db.Message(
        thread_id=thread_1,
        content="test message 3",
        role="user",
        timestamp=db.convert_dt_ts(datetime.now() + timedelta(days=1)),
    )
    message4 = db.Message(thread_id=thread_2, content="test message 4", role="user")
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
    message1 = db.Message(thread_id=thread_1, content="test message", role="user")
    message2 = db.Message(
        thread_id=thread_1,
        content="test message 2",
        role="assistant",
        timestamp=db.convert_dt_ts(datetime.now() + timedelta(days=1)),
    )
    message3 = db.Message(thread_id=thread_2, content="test message 3", role="user")
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
    message1 = db.Message(thread_id=thread_1, content="test message", role="user")
    message2 = db.Message(
        thread_id=thread_1,
        content="test message 2",
        role="assistant",
        timestamp=db.convert_dt_ts(datetime.now() + timedelta(days=1)),
    )
    message3 = db.Message(thread_id=thread_2, content="test message 3", role="user")
    message1_id = db.insert_message(message1)
    message2_id = db.insert_message(message2)
    message3_id = db.insert_message(message3)
    message_patch = db.Message(
        id=message2_id,
        content="test message patched",
        timestamp=db.convert_dt_ts(datetime.now()),
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


def test_delete_message_db(db_init: str, message_1: db.Message) -> None:
    """
    Test the delete_message function.
    """
    assert message_1["id"]
    db.delete_message(message_1["id"])
    with pytest.raises(ValueError):
        db.select_message(message_1["id"])
