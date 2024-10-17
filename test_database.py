"""
This file contains the tests for the database.py file.
"""

import os

from database import DB


def test_post_message() -> None:
    """
    Test the post_message method of the DB class.
    """
    db = DB("test_database.db")
    db.post_message("user", "chatbot", "test message")
    db.post_message("user2", "chatbot2", "test message2")
    messages = db.get_messages()
    assert messages[0][0] == 1
    assert messages[0][2] == "user"
    assert messages[0][3] == "chatbot"
    assert messages[0][4] == "test message"
    assert messages[1][0] == 2
    assert messages[1][2] == "user2"
    assert messages[1][3] == "chatbot2"
    assert messages[1][4] == "test message2"
    db.conn.close()
    os.remove("test_database.db")
