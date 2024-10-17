"""
This file contains the tests for the database.py file.
"""

import os

from database import DB


def test_create_database() -> None:
    """
    Test the creation of the database.
    """
    db = DB("test_database.db")
    db.conn.close()
    assert os.path.exists("test_database.db")
    os.remove("test_database.db")


def test_post_thread() -> None:
    """
    Test the post_thread method of the DB class.
    """
    db = DB("test_database_1.db")
    thread_id = db.post_thread("user", "chatbot")
    assert thread_id == 1
    thread_id = db.post_thread("user2", "chatbot2")
    assert thread_id == 2
    db.conn.close()
    os.remove("test_database_1.db")


def test_get_latest_thread() -> None:
    """
    Test the get_latest_thread method of the DB class.
    """
    db = DB("test_database_2.db")
    db.post_thread("user", "chatbot")
    thread_id = db.post_thread("user", "chatbot")
    latest_thread = db.get_latest_thread("user", "chatbot")
    assert latest_thread == thread_id
    latest_thread = db.get_latest_thread("user2", "chatbot2")
    assert latest_thread == 0
    db.conn.close()
    os.remove("test_database_2.db")


def test_post_message() -> None:
    """
    Test the post_message method of the DB class.
    """
    db = DB("test_database_3.db")
    thread_id = db.post_thread("user", "chatbot")
    db.post_message(thread_id, "test message")
    db.conn.close()
    os.remove("test_database_3.db")


def test_get_messages() -> None:
    """
    Test the get_messages method of the DB class.
    """
    db = DB("test_database_4.db")
    thread_id = db.post_thread("user", "chatbot")
    thread_id2 = db.post_thread("user2", "chatbot2")
    db.post_message(thread_id, "test message")
    db.post_message(thread_id2, "test message2")
    messages = db.get_messages()
    print(messages)
    assert messages[0][0] == 1
    assert messages[0][2] == thread_id
    assert messages[0][3] == "test message"
    assert messages[1][0] == 2
    assert messages[1][2] == thread_id2
    assert messages[1][3] == "test message2"
    db.conn.close()
    os.remove("test_database_4.db")
