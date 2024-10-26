"""
This file contains the tests for the auth/passwords.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

import pytest

import auth
import database as db
from tests.test_database.test_main import db_init
from tests.test_database.test_users import user


def test_insert_user(db_init: str, user: db.User) -> None:
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


def test_authenticate_user(db_init: str, user: db.User) -> None:
    """
    Test the authenticate_user function.
    """
    auth.insert_user(user)
    assert auth.authenticate_user("test_user", "password")
    assert not auth.authenticate_user("test_user", "wrong_password")
    with pytest.raises(ValueError):
        auth.authenticate_user("unknown_user", "password")
