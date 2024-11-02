"""Tests for the threads module in the database package."""

# pylint: disable=redefined-outer-name unused-argument unused-import

import time
from typing import List

import database as db

from .fixtures import character, characters, user
from .test_main import test_db


def test_insert_thread(user: db.User, character: db.Character) -> None:
    """Test the insert_thread function."""
    thread = db.Thread(
        user_id=user["id"],
        char_id=character["id"],
    )
    result = db.insert_thread(thread)
    assert result == 1


def test_select_thread(user: db.User, character: db.Character) -> None:
    """Test the select_thread function."""
    thread = db.Thread(
        user_id=user["id"],
        char_id=character["id"],
    )
    thread_id = db.insert_thread(thread)
    result = db.select_thread(thread_id)
    assert result["user_id"] == user["id"]
    assert result["char_id"] == character["id"]


def test_select_threads_without_query(
    user: db.User, characters: List[db.Character]
) -> None:
    """Test the select_threads function without a query."""
    thread = db.Thread(
        user_id=user["id"],
        char_id=characters[0]["id"],
    )
    thread2 = db.Thread(
        user_id=user["id"],
        char_id=characters[1]["id"],
    )
    db.insert_thread(thread)
    db.insert_thread(thread2)
    result = db.select_threads()
    assert len(result) == 2
    assert result[0]["user_id"] == user["id"]
    assert result[0]["char_id"] == characters[0]["id"]
    assert result[1]["user_id"] == user["id"]
    assert result[1]["char_id"] == characters[1]["id"]


def test_select_threads_with_query(
    user: db.User, characters: List[db.Character]
) -> None:
    """Test the select_threads function with a query."""
    thread = db.Thread(
        user_id=user["id"],
        char_id=characters[0]["id"],
    )
    thread2 = db.Thread(
        user_id=user["id"],
        char_id=characters[1]["id"],
    )
    thread3 = db.Thread(
        user_id=user["id"],
        char_id=characters[1]["id"],
    )
    thread4 = db.Thread(
        user_id=user["id"],
        char_id=characters[2]["id"],
    )
    db.insert_thread(thread)
    db.insert_thread(thread2)
    time.sleep(1)
    db.insert_thread(thread3)
    db.insert_thread(thread4)
    query = db.Thread(char_id=characters[1]["id"])
    options = db.QueryOptions(limit=2, orderby="started", order="desc")
    result = db.select_threads(query, options)
    assert len(result) == 2
    assert result[0]["user_id"] == user["id"]
    assert result[0]["char_id"] == characters[1]["id"]
    assert result[1]["user_id"] == user["id"]
    assert result[1]["char_id"] == characters[1]["id"]
    assert result[0]["started"] > result[1]["started"]


def test_select_latest_thread(user: db.User, character: db.Character) -> None:
    """Test the select_latest_thread function."""
    thread = db.Thread(
        user_id=user["id"],
        char_id=character["id"],
    )
    thread2 = db.Thread(
        user_id=user["id"],
        char_id=character["id"],
    )
    db.insert_thread(thread)
    time.sleep(1)
    latest_id = db.insert_thread(thread2)
    result = db.select_latest_thread(user["id"], character["id"])
    assert result["user_id"] == user["id"]
    assert result["char_id"] == character["id"]
    assert result["id"] == latest_id
