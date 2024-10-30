"""
This file contains the tests for the routes/threads.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import


from flask.testing import FlaskClient

import database as db
from tests.test_app import app, client
from tests.test_database.test_characters import char_1
from tests.test_database.test_main import db_init
from tests.test_database.test_messages import message_1
from tests.test_database.test_threads import thread_1
from tests.test_database.test_users import user_1


def test_new_thread(client: FlaskClient, user_1: db.User, char_1: db.Character) -> None:
    """Test the new thread route."""

    thread_payload = {
        "username": user_1["username"],
        "character": char_1["path_name"],
    }
    response = client.post("/v1/threads", json=thread_payload)
    assert response.status_code == 200
    assert response.data


def test_new_thread_missing_required_fields(client: FlaskClient) -> None:
    """Test the new thread route with missing required fields."""

    thread_payload = {
        "username": "test",
    }
    response = client.post("/v1/threads", json=thread_payload)
    assert response.status_code == 400
    assert response.data == b"missing required fields"


def test_new_thread_invalid_user(client: FlaskClient, char_1: db.Character) -> None:
    """Test the new thread route with an invalid user."""

    thread_payload = {
        "username": "test",
        "character": char_1["path_name"],
    }
    response = client.post("/v1/threads", json=thread_payload)
    assert response.status_code == 400
    assert response.data == b"user not found"


def test_new_thread_invalid_character(client: FlaskClient, user_1: db.User) -> None:
    """Test the new thread route with an invalid character."""

    thread_payload = {
        "username": user_1["username"],
        "character": "test",
    }
    response = client.post("/v1/threads", json=thread_payload)
    assert response.status_code == 400
    assert response.data == b"character not found"


def test_get_threads_by_user_app(
    client: FlaskClient, user_1: db.User, thread_1: db.Thread
) -> None:
    """Test the get threads by user route."""

    response = client.get(f"/v1/users/{user_1['username']}/threads")
    assert response.status_code == 200
    assert response.data


def test_get_latest_thread_by_user_app(
    client: FlaskClient, user_1: db.User, thread_1: db.Thread, message_1: db.Message
) -> None:
    """Test the get latest thread by user route."""

    response = client.get(f"/v1/users/{user_1['username']}/threads/latest")
    assert response.status_code == 200
    assert response.data
