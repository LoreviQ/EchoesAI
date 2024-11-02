"""Tests for the users module in the database package."""

# pylint: disable=redefined-outer-name unused-argument unused-import

import database as db

from .test_main import test_db


def test_insert_user(test_db: None) -> None:
    """Test the insert_user function."""
    user = db.User(
        username="test",
        password="test",
        email="test@test.com",
    )
    result = db.insert_user(user)
    assert result == 1


def test_select_user(test_db: None) -> None:
    """Test the select_user function."""
    user = db.User(
        username="test",
        password="test",
        email="test@test.com",
    )
    db.insert_user(user)
    result = db.select_user("test")
    assert result["username"] == "test"


def test_select_user_by_id(test_db: None) -> None:
    """Test the select_user_by_id function."""
    user = db.User(
        username="test",
        password="test",
        email="test@test.com",
    )
    uid = db.insert_user(user)
    result = db.select_user_by_id(uid)
    assert result["username"] == "test"


def test_update_user(test_db: None) -> None:
    """Test the update_user function."""
    user = db.User(
        username="test",
        password="test",
        email="test@test.com",
    )
    user["id"] = db.insert_user(user)
    user["username"] = "test2"
    db.update_user(user)
    result = db.select_user_by_id(user["id"])
    assert result["username"] == "test2"
