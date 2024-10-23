"""
This file contains the tests for the database/threads.py file.
"""

import os
import time
from typing import Generator, Tuple

import pytest

import database as db

# pylint: disable=redefined-outer-name unused-argument unused-import


@pytest.fixture
def chars(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[Tuple[db.Character, db.Character], None, None]:
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
    yield character_1, character_2
    os.remove(db_path)


def test_insert_thread(chars: Tuple[db.Character, db.Character]) -> None:
    """
    Test the insert_thread function.
    """
    assert chars[0]["id"]
    thread_id = db.insert_thread("user", chars[0]["id"])
    assert thread_id == 1
    thread_id = db.insert_thread("user2", chars[0]["id"])
    assert thread_id == 2


def test_select_thread(chars: Tuple[db.Character, db.Character]) -> None:
    """
    Test the select_thread function.
    """
    assert chars[0]["id"]
    thread_id = db.insert_thread("user", chars[0]["id"])
    thread = db.select_thread(thread_id)
    assert thread["user"] == "user"


def test_select_latest_thread(chars: Tuple[db.Character, db.Character]) -> None:
    """
    Test the select_latest_thread function.
    """
    assert chars[0]["id"]
    assert chars[1]["id"]
    db.insert_thread("user", chars[0]["id"])
    time.sleep(1)
    db.insert_thread("user", chars[0]["id"])
    thread_id = db.select_latest_thread("user", chars[0]["id"])
    assert thread_id == 2
    thread_id = db.select_latest_thread("user", chars[1]["id"])
    assert thread_id == 0


def test_select_threads_by_user(chars: Tuple[db.Character, db.Character]) -> None:
    """
    Test the select_threads_by_user function.
    """
    assert chars[0]["id"]
    db.insert_thread("user", chars[0]["id"])
    db.insert_thread("user", chars[0]["id"])
    db.insert_thread("user2", chars[0]["id"])
    threads = db.select_threads_by_user("user")
    assert len(threads) == 2
    threads = db.select_threads_by_user("user2")
    assert len(threads) == 1
    threads = db.select_threads_by_user("user3")
    assert len(threads) == 0
