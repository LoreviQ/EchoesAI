"""
This file contains the tests for the routes/users.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

from unittest.mock import MagicMock, patch

from flask.testing import FlaskClient

import auth
import database as db

from .fixtures import app, client


@patch("auth.insert_user")
@patch("auth.issue_access_token")
def test_post_user(
    mock_issue_access_token: MagicMock, mock_insert_user: MagicMock, client: FlaskClient
) -> None:
    """
    Test the post user route.
    """
    user_payload = {
        "username": "test_user",
        "password": "password",
        "email": "test@test.com",
    }
    token = b"test_token"
    mock_issue_access_token.return_value = token
    response = client.post("/v1/users", json=user_payload)
    assert response.status_code == 200
    assert response.data == token
    assert mock_insert_user.called_once_with(
        db.User(
            username=user_payload["username"],
            password=user_payload["password"],
            email=user_payload["email"],
        )
    )
    assert mock_issue_access_token.called_once_with(user_payload["username"])


def test_post_user_missing_field(client: FlaskClient) -> None:
    """
    Test the post user route with missing fields.
    """
    user_payload = {
        "username": "test_user",
        "password": "password",
    }
    response = client.post("/v1/users", json=user_payload)
    assert response.status_code == 400


@patch("auth.authenticate_user")
@patch("auth.issue_access_token")
def test_login(
    mock_issue_access_token: MagicMock,
    mock_authenticate_user: MagicMock,
    client: FlaskClient,
) -> None:
    """
    Test the login route.
    """
    mock_authenticate_user.return_value = True
    mock_issue_access_token.return_value = b"test_token"
    login_payload = {
        "username": "test_user",
        "password": "password",
    }
    response = client.post("/v1/login", json=login_payload)
    assert response.status_code == 200
    assert response.data == b"test_token"


@patch("auth.authenticate_user")
def test_login_invalid_user(
    mock_authenticate_user: MagicMock, client: FlaskClient
) -> None:
    """
    Test the login route with invalid user.
    """
    mock_authenticate_user.return_value = False
    login_payload = {
        "username": "test_user",
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


@patch("database.select_user")
@patch("database.select_threads")
@patch("database.select_character_by_id")
def get_threads_by_user(
    mock_select_character_by_id: MagicMock,
    mock_select_threads: MagicMock,
    mock_select_user: MagicMock,
    client: FlaskClient,
) -> None:
    """Test the get threads by user route."""
    user = db.User(id=1, username="test")
    character = db.Character(id=1, path_name="test_character")
    thread1 = db.Thread(id=1, user_id=user["id"], char_id=character["id"])
    thread2 = db.Thread(id=2, user_id=user["id"], char_id=character["id"])
    threads = [thread1, thread2]
    mock_select_user.return_value = user
    mock_select_threads.return_value = threads
    mock_select_character_by_id.return_value = character

    response = client.get(f"/v1/users/{user['username']}/threads")
    assert response.status_code == 200
    assert response.json
    assert len(response.json) == 2
    assert response.json[0]["id"] == thread1["id"]
    assert response.json[1]["id"] == thread2["id"]
    assert mock_select_user.called_once_with(user["username"])
    assert mock_select_threads.called_once_with(db.Thread(user_id=user["id"]), {})
    assert mock_select_character_by_id.called_once_with(thread1["char_id"])
