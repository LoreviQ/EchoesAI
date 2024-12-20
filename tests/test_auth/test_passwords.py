"""
This file contains the tests for the auth/passwords.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

import pytest

import auth
import database as db
from tests.test_database.test_main import test_db


def test_insert_user(test_db: str) -> None:
    """
    Test the insert_user function.
    """
    unhashed_password = "password"
    user = db.User(
        username="test_user", password=unhashed_password, email="test@test.com"
    )
    user_id = auth.insert_user(user)
    assert user_id == 1
    user_db = db.select_user("test_user")
    assert user_db["username"] == user["username"]
    assert user_db["email"] == user["email"]
    assert user_db["password"] != unhashed_password


def test_authenticate_user(test_db: str) -> None:
    """
    Test the authenticate_user function.
    """
    unhashed_password = "password"
    user = db.User(
        username="test_user", password=unhashed_password, email="test@test.com"
    )
    auth.insert_user(user)
    assert auth.authenticate_user("test_user", unhashed_password)
    assert not auth.authenticate_user("test_user", "wrong_password")
    with pytest.raises(ValueError):
        auth.authenticate_user("unknown_user", unhashed_password)
