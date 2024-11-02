"""
This file contains the tests for the routes/messages.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import


from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from flask.testing import FlaskClient

import database as db

from .fixtures import app, client


@patch("database.select_thread")
@patch("database.select_messages")
def test_get_messages_by_thread(
    mock_select_messages: MagicMock,
    mock_select_thread: MagicMock,
    client: FlaskClient,
) -> None:
    """Test the get messages by thread route."""
    thread_1 = db.Thread(id=1)
    message_1 = db.Message(id=1, thread_id=thread_1["id"], content="test message 1")
    message_2 = db.Message(id=2, thread_id=thread_1["id"], content="test message 2")
    mock_select_thread.return_value = thread_1
    mock_select_messages.return_value = [message_1, message_2]
    response = client.get(f"/v1/threads/{thread_1['id']}/messages")
    assert response.json
    assert response.json[0]["id"] == message_1["id"]
    assert response.json[1]["id"] == message_2["id"]
    assert response.status_code == 200
    assert mock_select_thread.called_once_with(thread_1["id"])
    assert mock_select_messages.called_once_with(db.Message(thread_id=thread_1["id"]))


@patch("database.select_thread")
@patch("database.select_messages")
def test_get_messages_by_thread_no_messages(
    mock_select_messages: MagicMock, mock_select_thread: MagicMock, client: FlaskClient
) -> None:
    """Test the get messages by thread route with no messages."""
    thread_1 = db.Thread(id=1)
    mock_select_thread.return_value = thread_1
    mock_select_messages.return_value = []
    response = client.get(f"/v1/threads/{thread_1['id']}/messages")
    assert response.json == []
    assert response.status_code == 200


@patch("database.select_thread")
def test_get_messages_by_thread_invalid_thread(
    mock_select_thread: MagicMock, client: FlaskClient
) -> None:
    """Test the get messages by thread route with an invalid thread."""
    mock_select_thread.side_effect = ValueError
    response = client.get("/v1/threads/0/messages")
    assert response.status_code == 404
    assert response.data == b"thread not found"


@patch("database.select_thread")
@patch("database.insert_message")
def test_post_message(
    mock_insert_message: MagicMock,
    mock_select_thread: MagicMock,
    client: FlaskClient,
) -> None:
    """Test the post message route."""
    thread_1 = db.Thread(id=1)
    mock_select_thread.return_value = thread_1
    message_payload = {
        "content": "test message",
        "role": "user",
    }
    response = client.post(
        f"/v1/threads/{thread_1['id']}/messages", json=message_payload
    )
    assert response.status_code == 200
    assert mock_insert_message.called_once_with(
        db.Message(
            thread_id=thread_1["id"],
            content=message_payload["content"],
            role=message_payload["role"],
        )
    )


@patch("database.select_thread")
def test_post_message_missing_required_fields(
    mock_select_thread: MagicMock, client: FlaskClient
) -> None:
    """Test the post message route with missing required fields."""
    thread_1 = db.Thread(id=1)
    mock_select_thread.return_value = thread_1
    message_payload = {
        "content": "test message",
    }
    response = client.post(
        f"/v1/threads/{thread_1['id']}/messages", json=message_payload
    )
    assert response.status_code == 400
    assert response.data == b"missing required fields"


@patch("database.select_thread")
def test_post_message_invalid_thread(
    mock_select_thread: MagicMock, client: FlaskClient
) -> None:
    """Test the post message route with an invalid thread."""
    mock_select_thread.side_effect = ValueError
    message_payload = {
        "content": "test message",
        "role": "user",
    }
    response = client.post("/v1/threads/0/messages", json=message_payload)
    assert response.status_code == 404


@patch("database.select_thread")
@patch("database.select_scheduled_message")
@patch("database.update_message")
def test_get_response_now_scheduled(
    mock_update_message: MagicMock,
    mock_select_scheduled_message: MagicMock,
    mock_select_thread: MagicMock,
    client: FlaskClient,
) -> None:
    """Tests the get response now route with a scheduled message."""
    now = datetime.now(timezone.utc)
    thread_1 = db.Thread(id=1)
    mock_select_thread.return_value = thread_1
    message_1 = db.Message(
        id=1,
        thread_id=thread_1["id"],
        content="test message",
        timestamp=now + timedelta(days=1),
    )
    mock_select_scheduled_message.return_value = message_1
    response = client.get(f"/v1/threads/{thread_1['id']}/message")
    assert response.status_code == 200
    assert mock_select_thread.called_once_with(thread_1["id"])
    assert mock_select_scheduled_message.called_once_with(thread_1["id"])
    assert mock_update_message.called_once


@patch("database.select_message")
@patch("database.delete_message")
def test_delete_message(
    mock_delete_message: MagicMock, mock_select_message: MagicMock, client: FlaskClient
) -> None:
    """Test the delete message route."""

    message_1 = db.Message(id=1, thread_id=1, content="test message")
    mock_select_message.return_value = message_1
    response = client.delete(f"/v1/messages/{message_1['id']}")
    assert response.status_code == 200
    assert mock_select_message.called_once_with(message_1["id"])
    assert mock_delete_message.called_once_with(message_1["id"])


@patch("database.select_message")
@patch("database.delete_messages_more_recent")
def test_delete_messages_more_recent_app(
    mock_delete_messages_more_recent: MagicMock,
    mock_select_message: MagicMock,
    client: FlaskClient,
) -> None:
    """Test the delete messages more recent route."""

    message_1 = db.Message(id=1, thread_id=1, content="test message")
    mock_select_message.return_value = message_1
    query = "?recent=true"
    response = client.delete(f"/v1/messages/{message_1['id']}{query}")
    assert response.status_code == 200
    assert mock_select_message.called_once_with(message_1["id"])
    assert mock_delete_messages_more_recent.called_once_with(message_1["id"])
