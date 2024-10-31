"""
This file contains the tests for the routes/messages.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import


import time

import pytest
from flask.testing import FlaskClient

import database as db
from tests.test_app import app, client
from tests.test_database.test_characters import char_1
from tests.test_database.test_main import db_init
from tests.test_database.test_messages import message_1, message_2, scheduled_message
from tests.test_database.test_threads import thread_1
from tests.test_database.test_users import user_1


def test_get_messages_by_thread(
    client: FlaskClient,
    thread_1: db.Thread,
    message_1: db.Message,
    message_2: db.Message,
) -> None:
    """Test the get messages by thread route."""

    response = client.get(f"/v1/threads/{thread_1['id']}/messages")
    assert response.json
    assert response.json[0]["id"] == message_1["id"]
    assert response.json[1]["id"] == message_2["id"]
    assert response.status_code == 200


def test_get_messages_by_thread_no_messages(
    client: FlaskClient, thread_1: db.Thread
) -> None:
    """Test the get messages by thread route with no messages."""

    response = client.get(f"/v1/threads/{thread_1['id']}/messages")
    assert response.json == []
    assert response.status_code == 200


def test_get_messages_by_thread_invalid_thread(client: FlaskClient) -> None:
    """Test the get messages by thread route with an invalid thread."""

    response = client.get("/v1/threads/0/messages")
    assert response.status_code == 404
    assert response.data == b"thread not found"


def test_post_message_app(client: FlaskClient, thread_1: db.Thread) -> None:
    """Test the post message route."""

    message_payload = {
        "content": "test message",
        "role": "user",
    }
    response = client.post(
        f"/v1/threads/{thread_1['id']}/messages", json=message_payload
    )
    assert response.status_code == 200

    # test that a response is generated
    time.sleep(3)
    response = client.get(f"/v1/threads/{thread_1['id']}/messages")
    assert response.status_code == 200
    assert response.json
    assert response.json[-1]["content"] == "Mock response"


def test_post_message_missing_required_fields(
    client: FlaskClient, thread_1: db.Thread
) -> None:
    """Test the post message route with missing required fields."""

    message_payload = {
        "content": "test message",
    }
    response = client.post(
        f"/v1/threads/{thread_1['id']}/messages", json=message_payload
    )
    assert response.status_code == 400
    assert response.data == b"missing required fields"


def test_post_message_invalid_thread(client: FlaskClient) -> None:
    """Test the post message route with an invalid thread."""

    message_payload = {
        "content": "test message",
        "role": "user",
    }
    response = client.post("/v1/threads/0/messages", json=message_payload)
    assert response.status_code == 404


def test_get_response_now_scheduled(
    client: FlaskClient, thread_1: db.Thread, scheduled_message: db.Message
) -> None:
    """Tests the get response now route with a scheduled message."""

    assert thread_1["id"]
    response = client.get(f"/v1/threads/{thread_1['id']}/message")
    assert response.status_code == 200
    messages = db.select_messages_by_thread(thread_1["id"])
    assert messages[-1]["content"] == scheduled_message["content"]


def test_get_response_now_generate(client: FlaskClient, thread_1: db.Thread) -> None:
    """Tests the get response now route without a scheduled message."""

    response = client.get(f"/v1/threads/{thread_1['id']}/message")
    assert response.status_code == 200
    time.sleep(2)
    response = client.get(f"/v1/threads/{thread_1['id']}/messages")
    assert response.status_code == 200
    assert response.json
    assert response.json[-1]["content"] == "Mock response"


def test_get_response_now_invalid_thread(client: FlaskClient) -> None:
    """Tests the get response now route with an invalid thread."""

    response = client.get("/v1/threads/0/message")
    assert response.status_code == 404
    assert response.data == b"thread not found"


def test_delete_message(
    client: FlaskClient,
    message_1: db.Message,
) -> None:
    """Test the delete message route."""

    assert message_1["id"]
    response = client.delete(f"/v1/messages/{message_1['id']}")
    assert response.status_code == 200
    with pytest.raises(ValueError):
        db.select_message(message_1["id"])


def test_delete_messages_more_recent_app(
    client: FlaskClient,
    message_1: db.Message,
    message_2: db.Message,
    scheduled_message: db.Message,
) -> None:
    """Test the delete messages more recent route."""

    assert message_2["id"]
    assert message_1["thread_id"]
    query = "?recent=true"
    response = client.delete(f"/v1/messages/{message_2['id']}{query}")
    assert response.status_code == 200
    response = client.get(f"/v1/threads/{message_1['thread_id']}/messages")
    assert response.json
    assert len(response.json) == 1


def test_delete_messages_more_recent_invalid_message(client: FlaskClient) -> None:
    """Test the delete messages more recent route with an invalid message."""

    response = client.delete("/v1/messages/0")
    assert response.status_code == 404
    assert response.data == b"message not found"
