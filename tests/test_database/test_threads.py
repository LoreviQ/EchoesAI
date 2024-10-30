"""
This file contains the tests for the database/threads.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import


import time
from typing import Generator, List

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


@pytest.fixture
def many_threads(
    user_1: db.User, user_2: db.User, char_1: db.Character, char_2: db.Character
) -> Generator[List[db.Thread], None, None]:
    """
    Generates a large list of threads for query testing.
    """
    assert char_1["id"]
    assert char_2["id"]
    assert user_1["id"]
    assert user_2["id"]
    t1 = db.insert_thread(user_1["id"], char_1["id"])
    t2 = db.insert_thread(user_1["id"], char_1["id"])
    t3 = db.insert_thread(user_2["id"], char_1["id"])
    t4 = db.insert_thread(user_2["id"], char_2["id"])
    t5 = db.insert_thread(user_2["id"], char_2["id"])
    db.insert_message(db.Message(thread_id=t1, content="Test", role="user"))
    db.insert_message(db.Message(thread_id=t2, content="Test", role="user"))
    db.insert_message(db.Message(thread_id=t3, content="Test", role="user"))
    db.insert_message(db.Message(thread_id=t4, content="Test", role="user"))
    db.insert_message(db.Message(thread_id=t5, content="Test", role="user"))
    threads = db.select_threads(db.Thread(), db.QueryOptions())
    yield threads


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


def test_select_latest_thread_by_user(
    db_init: str, user_1: db.User, char_1: db.Character
) -> None:
    """Test the select_latest_thread_by_user function."""
    assert char_1["id"]
    assert user_1["id"]
    thread_id_1 = db.insert_thread(user_1["id"], char_1["id"])
    thread_id_2 = db.insert_thread(user_1["id"], char_1["id"])
    db.insert_message(db.Message(thread_id=thread_id_1, content="Test", role="user"))
    time.sleep(1)
    db.insert_message(db.Message(thread_id=thread_id_2, content="Test", role="user"))
    latest_thread = db.select_latest_thread_by_user(user_1["id"])
    assert latest_thread["id"] == thread_id_2
    time.sleep(1)
    db.insert_message(db.Message(thread_id=thread_id_1, content="Test", role="user"))
    latest_thread = db.select_latest_thread_by_user(user_1["id"])
    assert latest_thread["id"] == thread_id_1


def test_select_threads_without_query(
    db_init: str, thread_1: db.Thread, thread_2: db.Thread
) -> None:
    """Test the select_threads function without a query."""
    threads = db.select_threads(db.Thread(), db.QueryOptions())
    assert len(threads) == 2


def test_select_threads_with_user_query(
    db_init: str, user_1: db.User, many_threads: List[db.Thread]
) -> None:
    """Test the select_threads function with a user query."""
    threads = db.select_threads(db.Thread(user_id=user_1["id"]), db.QueryOptions())
    assert len(threads) == 2


def test_select_threads_with_order_by(
    db_init: str, many_threads: List[db.Thread]
) -> None:
    """Test the select_threads function with an order by query."""
    threads = db.select_threads(
        db.Thread(),
        db.QueryOptions(orderby="id", order="DESC"),
    )
    assert threads[0]["id"] == 5
    assert threads[1]["id"] == 4
    assert threads[2]["id"] == 3
    assert threads[3]["id"] == 2
    assert threads[4]["id"] == 1


def test_select_threads_with_limit(db_init: str, many_threads: List[db.Thread]) -> None:
    """Test the select_threads function with a limit query."""
    threads = db.select_threads(
        db.Thread(),
        db.QueryOptions(limit=3),
    )
    assert len(threads) == 3
