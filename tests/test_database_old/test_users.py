"""
This file contains the tests for the database/users.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

from typing import Generator

import pytest

import auth
import database_old as db
from tests.test_database_old.test_main import db_init


@pytest.fixture
def user_1() -> Generator[db.User, None, None]:
    """
    Yields a user to be used in testing.
    """
    password = "password"
    user = db.User(username="test_user", password=password, email="test@test.com")
    user["id"] = auth.insert_user(user)
    user["password"] = password
    yield user


@pytest.fixture
def user_2() -> Generator[db.User, None, None]:
    """
    Yields a user distinct from user_1 to be used in testing.
    """
    password = "password_2"
    user = db.User(username="test_user_2", password=password, email="test_2@test.com")
    user["id"] = auth.insert_user(user)
    user["password"] = password
    yield user


def test_insert_user(db_init: str) -> None:
    """
    Test the insert_user function.
    """
    user = db.User(username="test_user", password="password", email="test@test.com")
    user_id = db.insert_user(user)
    assert user_id == 1


def test_select_user(db_init: str) -> None:
    """
    Test the select_user function.
    """
    user = db.User(username="test_user", password="password", email="test@test.com")
    db.insert_user(user)
    selected_user = db.select_user("test_user")
    assert selected_user["username"] == "test_user"


def test_update_user(db_init: str) -> None:
    """
    Test the update_user function.
    """
    user = db.User(username="test_user", password="password", email="test@test.com")
    db.insert_user(user)
    user["password"] = "new_password"
    db.update_user(user)
    updated_user = db.select_user("test_user")
    assert updated_user["password"] == "new_password"
