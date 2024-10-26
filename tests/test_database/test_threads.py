"""
This file contains the tests for the database/threads.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

import os
import time
from typing import Generator, Tuple

import pytest

import database as db
from tests.test_database.test_characters import char_1, char_1_ins, char_2, char_2_ins
from tests.test_database.test_main import db_init


def test_insert_thread(db_init: str, char_1_ins: db.Character) -> None:
    """
    Test the insert_thread function.
    """
    assert char_1_ins["id"]
    thread_id = db.insert_thread("user", char_1_ins["id"])
    assert thread_id == 1
    thread_id = db.insert_thread("user2", char_1_ins["id"])
    assert thread_id == 2


def test_select_thread(db_init: str, char_1_ins: db.Character) -> None:
    """
    Test the select_thread function.
    """
    assert char_1_ins["id"]
    thread_id = db.insert_thread("user", char_1_ins["id"])
    thread = db.select_thread(thread_id)
    assert thread["user"] == "user"


def test_select_latest_thread(
    db_init: str, char_1_ins: db.Character, char_2_ins: db.Character
) -> None:
    """
    Test the select_latest_thread function.
    """
    assert char_1_ins["id"]
    assert char_2_ins["id"]
    db.insert_thread("user", char_1_ins["id"])
    time.sleep(1)
    db.insert_thread("user", char_1_ins["id"])
    thread_id = db.select_latest_thread("user", char_1_ins["id"])
    assert thread_id == 2
    thread_id = db.select_latest_thread("user", char_2_ins["id"])
    assert thread_id == 0


def test_select_threads_by_user(db_init: str, char_1_ins: db.Character) -> None:
    """
    Test the select_threads_by_user function.
    """
    assert char_1_ins["id"]
    db.insert_thread("user", char_1_ins["id"])
    db.insert_thread("user", char_1_ins["id"])
    db.insert_thread("user2", char_1_ins["id"])
    threads = db.select_threads_by_user("user")
    assert len(threads) == 2
    threads = db.select_threads_by_user("user2")
    assert len(threads) == 1
    threads = db.select_threads_by_user("user3")
    assert len(threads) == 0
