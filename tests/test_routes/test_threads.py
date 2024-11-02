"""
This file contains the tests for the routes/threads.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import


from unittest.mock import MagicMock, patch

from flask.testing import FlaskClient

import database as db

from .fixtures import app, client


@patch("database.select_character")
@patch("database.select_user")
@patch("database.insert_thread")
def test_new_thread(
    mock_insert_thread: MagicMock,
    mock_select_user: MagicMock,
    mock_select_character: MagicMock,
    client: FlaskClient,
) -> None:
    """Test the new thread route."""
    user = db.User(id=1, username="test")
    mock_select_user.return_value = user
    character = db.Character(id=1, path_name="test_character")
    mock_select_character.return_value = character
    thread_payload = {
        "username": user["username"],
        "character": character["path_name"],
    }
    mock_insert_thread.return_value = 1
    response = client.post("/v1/threads", json=thread_payload)
    assert response.status_code == 200
    assert mock_select_user.called_once_with(user["username"])
    assert mock_select_character.called_once_with(character["path_name"])
    assert mock_insert_thread.called_once_with(
        db.Thread(user_id=user["id"], char_id=character["id"])
    )
    assert response.data == b"1"


def test_new_thread_missing_required_fields(client: FlaskClient) -> None:
    """Test the new thread route with missing required fields."""

    thread_payload = {
        "username": "test",
    }
    response = client.post("/v1/threads", json=thread_payload)
    assert response.status_code == 400
    assert response.data == b"missing required fields"


@patch("database.select_user")
def test_new_thread_invalid_user(
    mock_select_user: MagicMock, client: FlaskClient
) -> None:
    """Test the new thread route with an invalid user."""
    mock_select_user.side_effect = ValueError
    thread_payload = {
        "username": "test",
        "character": "test_character",
    }
    response = client.post("/v1/threads", json=thread_payload)
    assert response.status_code == 400
    assert response.data == b"invalid payload"


@patch("database.select_threads")
@patch("database.select_user")
@patch("database.select_character")
def test_get_threads_with_query(
    mock_select_character: MagicMock,
    mock_select_user: MagicMock,
    mock_select_threads: MagicMock,
    client: FlaskClient,
) -> None:
    """Test the get threads without query route."""
    user = db.User(id=1, username="test")
    character = db.Character(id=1, path_name="test_character")
    mock_select_user.return_value = user
    mock_select_character.return_value = character
    mock_select_threads.return_value = []
    query = f"?username={user['username']}&char_path={character['path_name']}&limit=1"
    response = client.get(f"/v1/threads{query}")
    assert response.status_code == 200
    assert mock_select_threads.called_once_with(
        db.Thread(user_id=user["id"], char_id=character["id"]),
        db.QueryOptions(limit=1),
    )
