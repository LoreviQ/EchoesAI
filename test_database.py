"""
This file contains the tests for the database.py file.
"""

# pylint: disable=redefined-outer-name
import os
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
    db.conn.close()
    os.remove(db_path)


def test_create_database() -> None:
    """
    Test the creation of the database.
    """
    db = DB("test_database.db")
    db.conn.close()
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
    user, chatbot = db.get_thread(thread_id)
    assert user == "user"
    assert chatbot == "chatbot"
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
    assert len(threads) == 2
    assert threads[0][0] == 1
    assert threads[0][1] == "chatbot"
    assert threads[1][0] == 2
    assert threads[1][1] == "chatbot2"
    threads = db.get_threads_by_user("user2")
    assert len(threads) == 1
    assert threads[0][0] == 3
    assert threads[0][1] == "chatbot"


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
    assert messages[0][0] == "test message"
    assert messages[0][1] == "user"
    assert messages[1][0] == "test message2"
    assert messages[1][1] == "assistant"


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
    assert messages[0][0] == "test message"
    messages = db.get_messages_by_thread(thread_id2)
    assert len(messages) == 1
    assert messages[0][0] == "test message2"
