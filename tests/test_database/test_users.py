"""
This file contains the tests for the database/users.py file.
"""

import os
from typing import Generator

import pytest

import database as db

# pylint: disable=redefined-outer-name unused-argument unused-import


@pytest.fixture
def user(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[db.User, None, None]:
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
    user = db.User(username="test_user", password="password", email="test@test.com")
    yield user
    os.remove(db_path)


def test_insert_user(user: db.User) -> None:
    """
    Test the insert_user function.
    """
    user_id = db.insert_user(user)
    assert user_id == 1


def test_select_user(user: db.User) -> None:
    """
    Test the select_user function.
    """
    db.insert_user(user)
    selected_user = db.select_user("test_user")
    assert selected_user["username"] == "test_user"


def test_update_user(user: db.User) -> None:
    """
    Test the update_user function.
    """
    db.insert_user(user)
    user["password"] = "new_password"
    db.update_user(user)
    updated_user = db.select_user("test_user")
    assert updated_user["password"] == "new_password"
