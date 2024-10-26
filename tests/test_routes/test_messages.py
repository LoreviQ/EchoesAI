"""
This file contains the tests for the routes/messages.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import


import time

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

    response = client.get(f"/threads/{thread_1['id']}/messages")
    assert response.json
    assert response.json[0]["id"] == message_1["id"]
    assert response.json[1]["id"] == message_2["id"]
    assert response.status_code == 200


def test_get_messages_by_thread_no_messages(
    client: FlaskClient, thread_1: db.Thread
) -> None:
    """Test the get messages by thread route with no messages."""

    response = client.get(f"/threads/{thread_1['id']}/messages")
    assert response.json == []
    assert response.status_code == 200


def test_get_messages_by_thread_invalid_thread(client: FlaskClient) -> None:
    """Test the get messages by thread route with an invalid thread."""

    response = client.get("/threads/0/messages")
    assert response.status_code == 404
    assert response.data == b"thread not found"


def test_post_message(client: FlaskClient, thread_1: db.Thread) -> None:
    """Test the post message route."""

    message_payload = {
        "content": "test message",
        "role": "user",
    }
    response = client.post(f"/threads/{thread_1['id']}/messages", json=message_payload)
    assert response.status_code == 200


def test_post_message_missing_required_fields(
    client: FlaskClient, thread_1: db.Thread
) -> None:
    """Test the post message route with missing required fields."""

    message_payload = {
        "content": "test message",
    }
    response = client.post(f"/threads/{thread_1['id']}/messages", json=message_payload)
    assert response.status_code == 400
    assert response.data == b"missing required fields"


def test_post_message_invalid_thread(client: FlaskClient) -> None:
    """Test the post message route with an invalid thread."""

    message_payload = {
        "content": "test message",
        "role": "user",
    }
    response = client.post("/threads/0/messages", json=message_payload)
    assert response.status_code == 404


def test_response_generation(client: FlaskClient, thread_1: db.Thread) -> None:
    """Test that a response is generated when messaged."""

    message_payload = {
        "content": "test message",
        "role": "user",
    }
    response = client.post(f"/threads/{thread_1['id']}/messages", json=message_payload)
    assert response.status_code == 200
    time.sleep(3)
    response = client.get(f"/threads/{thread_1['id']}/messages")
    assert response.status_code == 200
    assert response.json[-1]["content"] == "Mock response"


def test_get_response_now_scheduled(
    client: FlaskClient, thread_1: db.Thread, scheduled_message: db.Message
) -> None:
    """Tests the get response now route with a scheduled message."""

    response = client.get(f"/threads/{thread_1['id']}/messages/new")
    assert response.status_code == 200
    messages = db.select_messages_by_thread(thread_1["id"])
    assert messages[-1]["content"] == scheduled_message["content"]


def test_get_response_now_generate(client: FlaskClient, thread_1: db.Thread) -> None:
    """Tests the get response now route without a scheduled message."""

    response = client.get(f"/threads/{thread_1['id']}/messages/new")
    assert response.status_code == 200
    time.sleep(2)
    response = client.get(f"/threads/{thread_1['id']}/messages")
    assert response.status_code == 200
    assert response.json[-1]["content"] == "Mock response"


def test_get_response_now_invalid_thread(client: FlaskClient) -> None:
    """Tests the get response now route with an invalid thread."""

    response = client.get("/threads/0/messages/new")
    assert response.status_code == 404
    assert response.data == b"thread not found"


def test_delete_messages_more_recent(
    client: FlaskClient,
    message_1: db.Message,
    message_2: db.Message,
    scheduled_message: db.Message,
) -> None:
    """Test the delete messages more recent route."""

    response = client.delete(f"/messages/{message_2['id']}")
    assert response.status_code == 200
    response = client.get(f"/threads/{message_1['thread']['id']}/messages")
    assert len(response.json) == 1


def test_delete_messages_more_recent_invalid_message(client: FlaskClient) -> None:
    """Test the delete messages more recent route with an invalid message."""

    response = client.delete("/messages/0")
    assert response.status_code == 404
    assert response.data == b"message not found"
