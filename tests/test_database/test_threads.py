"""
This file contains the tests for the database/threads.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import


import time
from typing import Generator

import pytest

import database as db
from tests.test_database.test_characters import char_1, char_2
from tests.test_database.test_main import db_init
from tests.test_database.test_users import user_1, user_2


@pytest.fixture
def thread_1(user_1: db.User, char_1: db.Character) -> Generator[db.Thread, None, None]:
    """
    Creates a thread to be used in testing.
    """
    assert char_1["id"]
    assert user_1["id"]
    thread_id = db.insert_thread(user_1["id"], char_1["id"])
    thread = db.select_thread(thread_id)
    yield thread


@pytest.fixture
def thread_2(user_2: db.User, char_2: db.Character) -> Generator[db.Thread, None, None]:
    """
    Creates a thread distinct from thread_1 to be used in testing.
    """
    assert char_2["id"]
    assert user_2["id"]
    thread_id = db.insert_thread(user_2["id"], char_2["id"])
    thread = db.select_thread(thread_id)
    yield thread


def test_insert_thread(
    db_init: str, user_1: db.User, user_2: db.User, char_1: db.Character
) -> None:
    """
    Test the insert_thread function.
    """
    assert char_1["id"]
    assert user_1["id"]
    assert user_2["id"]
    thread_id = db.insert_thread(user_1["id"], char_1["id"])
    assert thread_id == 1
    thread_id = db.insert_thread(user_2["id"], char_1["id"])
    assert thread_id == 2


def test_select_thread(db_init: str, user_1: db.User, char_1: db.Character) -> None:
    """
    Test the select_thread function.
    """
    assert char_1["id"]
    assert user_1["id"]
    thread_id = db.insert_thread(user_1["id"], char_1["id"])
    thread = db.select_thread(thread_id)
    assert thread["user_id"] == user_1["id"]


def test_select_latest_thread(
    db_init: str, user_1: db.User, char_1: db.Character, char_2: db.Character
) -> None:
    """
    Test the select_latest_thread function.
    """
    assert char_1["id"]
    assert char_2["id"]
    assert user_1["id"]
    db.insert_thread(user_1["id"], char_1["id"])
    time.sleep(1)
    db.insert_thread(user_1["id"], char_1["id"])
    thread_id = db.select_latest_thread(user_1["id"], char_1["id"])
    assert thread_id == 2
    thread_id = db.select_latest_thread(user_1["id"], char_2["id"])
    assert thread_id == 0


def test_select_threads_by_user(
    db_init: str, user_1: db.User, user_2: db.User, char_1: db.Character
) -> None:
    """
    Test the select_threads_by_user function.
    """
    assert char_1["id"]
    assert user_1["id"]
    assert user_2["id"]
    db.insert_thread(user_1["id"], char_1["id"])
    db.insert_thread(user_1["id"], char_1["id"])
    db.insert_thread(user_2["id"], char_1["id"])
    threads = db.select_threads_by_user(user_1["id"])
    assert len(threads) == 2
    threads = db.select_threads_by_user(user_2["id"])
    assert len(threads) == 1
    threads = db.select_threads_by_user(0)
    assert len(threads) == 0
