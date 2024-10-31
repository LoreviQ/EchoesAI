"""
This file contains the tests for the routes/threads.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import


from flask.testing import FlaskClient

import database_old as db
from not_t.test_app import app, client
from not_t.test_database_old.test_characters import char_1, char_2
from not_t.test_database_old.test_main import db_init
from not_t.test_database_old.test_messages import message_1
from not_t.test_database_old.test_threads import many_threads, thread_1
from not_t.test_database_old.test_users import user_1, user_2


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


def test_get_threads_without_query_app(
    client: FlaskClient, many_threads: db.Thread
) -> None:
    """Test the get threads without query route."""

    response = client.get("/v1/threads")
    assert response.status_code == 200
    assert response.data
    assert len(response.json) == 5


def test_get_threads_with_query_app(
    client: FlaskClient, user_1: db.User, char_1: db.Character, many_threads: db.Thread
) -> None:
    """Test the get threads without query route."""

    query = f"?username={user_1['username']}&char_path={char_1['path_name']}&limit=1"
    response = client.get(f"/v1/threads{query}")
    assert response.status_code == 200
    assert response.data
    assert len(response.json) == 1
    assert response.json[0]["user_id"] == user_1["id"]
    assert response.json[0]["char_id"] == char_1["id"]
