"""
This file contains the tests for the database/users.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

from typing import Generator

import pytest

import database as db
from tests.test_database.test_main import db_init


@pytest.fixture
def user() -> Generator[db.User, None, None]:
    """
    Yields a user to be used in testing.
    """
    user = db.User(username="test_user", password="password", email="test@test.com")
    yield user


def test_insert_user(db_init: str, user: db.User) -> None:
    """
    Test the insert_user function.
    """
    user_id = db.insert_user(user)
    assert user_id == 1


def test_select_user(db_init: str, user: db.User) -> None:
    """
    Test the select_user function.
    """
    db.insert_user(user)
    selected_user = db.select_user("test_user")
    assert selected_user["username"] == "test_user"


def test_update_user(db_init: str, user: db.User) -> None:
    """
    Test the update_user function.
    """
    db.insert_user(user)
    user["password"] = "new_password"
    db.update_user(user)
    updated_user = db.select_user("test_user")
    assert updated_user["password"] == "new_password"
