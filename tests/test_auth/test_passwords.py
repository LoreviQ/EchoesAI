"""
This file contains the tests for the auth/passwords.py file.
"""

import os
from typing import Generator

import pytest

import auth
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
    original_password = user["password"]
    user_id = auth.insert_user(user)
    assert user_id == 1
    user_db = db.select_user("test_user")
    assert user_db["username"] == user["username"]
    assert user_db["email"] == user["email"]
    assert user_db["password"] != original_password


def test_authenticate_user(user: db.User) -> None:
    """
    Test the authenticate_user function.
    """
    auth.insert_user(user)
    assert auth.authenticate_user("test_user", "password")
    assert not auth.authenticate_user("test_user", "wrong_password")
    with pytest.raises(ValueError):
        auth.authenticate_user("unknown_user", "password")
