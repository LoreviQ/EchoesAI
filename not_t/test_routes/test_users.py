"""
This file contains the tests for the routes/users.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import


from flask.testing import FlaskClient

import auth
import database_old as db
from not_t.test_app import app, client
from not_t.test_database_old.test_main import db_init
from not_t.test_database_old.test_users import user_1, user_2


def test_new_user(client: FlaskClient) -> None:
    """
    Test the new user route.
    """
    user_payload = {
        "username": "test_user",
        "password": "password",
        "email": "test@test.com",
    }
    response = client.post("/v1/users", json=user_payload)
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
    response = client.post("/v1/users", json=user_payload)
    assert response.status_code == 400


def test_login(client: FlaskClient, user_1: db.User) -> None:
    """
    Test the login route.
    """
    login_payload = {
        "username": user_1["username"],
        "password": user_1["password"],
    }
    response = client.post("/v1/login", json=login_payload)
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
    response = client.post("/v1/login", json=login_payload)
    assert response.status_code == 401
    assert not response.data


def test_login_missing_field(client: FlaskClient) -> None:
    """
    Test the login route with missing fields.
    """
    login_payload = {
        "username": "test_user",
    }
    response = client.post("/v1/login", json=login_payload)
    assert response.status_code == 400


def get_threads_by_user(
    client: FlaskClient, user_1: db.User, thread_1: db.Thread
) -> None:
    """Test the get threads by user route."""

    response = client.get(f"/v1/users/{user_1['username']}/threads")
    assert response.status_code == 200
    assert response.json
    assert response.json[0]["id"] == thread_1["id"]
    assert response.json[0]["user"] == user_1["username"]


def test_get_threads_by_user_no_threads(client: FlaskClient, user_1: db.User) -> None:
    """Test the get threads by user route with no threads."""
    response = client.get(f"/v1/users/{user_1['username']}/threads")
    assert response.status_code == 200
    assert response.json == []


def test_get_threads_by_user_invalid_user(client: FlaskClient) -> None:
    """Test the get threads by user route with an invalid user."""
    response = client.get("/v1/users/not_a_user/threads")
    assert response.status_code == 400
    assert response.data == b"user not found"
