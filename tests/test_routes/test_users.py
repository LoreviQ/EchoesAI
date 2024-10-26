"""
This file contains the tests for the routes/users.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import


from flask.testing import FlaskClient

import auth
import database as db
from tests.test_app import app, client
from tests.test_database.test_main import db_init
from tests.test_database.test_users import user_1, user_2


def test_new_user(client: FlaskClient) -> None:
    """
    Test the new user route.
    """
    user_payload = {
        "username": "test_user",
        "password": "password",
        "email": "test@test.com",
    }
    response = client.post("/users/new", json=user_payload)
    assert response.status_code == 200
    assert response.data
    token = response.data
    user = auth.auth_access_token(token)
    assert user == user_payload["username"]


def test_new_user_missing_field(client: FlaskClient) -> None:
    """
    Test the new user route with missing fields.
    """
    user_payload = {
        "username": "test_user",
        "password": "password",
    }
    response = client.post("/users/new", json=user_payload)
    assert response.status_code == 400


def test_login(client: FlaskClient, user_1: db.User) -> None:
    """
    Test the login route.
    """
    login_payload = {
        "username": user_1["username"],
        "password": user_1["password"],
    }
    response = client.post("/login", json=login_payload)
    assert response.status_code == 200
    assert response.data
    token = response.data
    user = auth.auth_access_token(token)
    assert user == user_1["username"]


def test_login_invalid_user(client: FlaskClient, user_1: db.User) -> None:
    """
    Test the login route with invalid user.
    """
    login_payload = {
        "username": user_1["username"],
        "password": "invalid_password",
    }
    response = client.post("/login", json=login_payload)
    assert response.status_code == 401
    assert not response.data


def test_login_missing_field(client: FlaskClient) -> None:
    """
    Test the login route with missing fields.
    """
    login_payload = {
        "username": "test_user",
    }
    response = client.post("/login", json=login_payload)
    assert response.status_code == 400
