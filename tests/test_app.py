"""
This file contains the tests for the app.py file.
"""

# pylint: disable=redefined-outer-name

import os
import time
from datetime import datetime, timedelta, timezone
from multiprocessing import Value
from typing import Generator

import pytest
from flask.testing import FlaskClient

from app import App
from model import Model, ModelMocked

# Shared counter for port numbers
port_counter = Value("i", 5000)


@pytest.fixture
def app() -> Generator[App, None, None]:
    """
    Create an App object for testing and teardown after testing.
    """
    test_name = os.environ.get("PYTEST_CURRENT_TEST")
    if test_name is None:
        test_name = "unknown"
    else:
        test_name = test_name.split(":")[-1].split(" ")[0]
    db_path = f"test_database_{test_name}.db"
    with port_counter.get_lock():
        port = port_counter.value
        port_counter.value += 1
    model = Model(ModelMocked("short"))
    app = App(db_path=db_path, model=model, port=port)
    yield app
    os.remove(db_path)


@pytest.fixture
def client(app: App) -> Generator[FlaskClient, None, None]:
    """
    Create a Flask test client for testing and teardown after testing.
    """
    with app.app.test_client() as client:
        yield client


def test_ready(client: FlaskClient) -> None:
    """
    Test the readiness route.
    """
    response = client.get("/readiness")
    assert response.status_code == 200


def test_new_thread(client: FlaskClient) -> None:
    """
    Test the new thread route.
    """
    response = client.post(
        "/threads/new",
        json={"username": "user", "character": "test"},
    )
    assert response.status_code == 200
    assert response.data == b"1"


def test_get_threads_by_user(app: App, client: FlaskClient) -> None:
    """
    Test the get threads by user route.
    """
    app.db.post_thread("user", "test")
    app.db.post_thread("user", "test2")
    response = client.get("/threads/user")
    assert response.status_code == 200
    assert response.json == [
        {"id": 1, "user": "user", "chatbot": "test", "phase": 0},
        {"id": 2, "user": "user", "chatbot": "test2", "phase": 0},
    ]


def test_get_messages_by_thread(app: App, client: FlaskClient) -> None:
    """
    Test the get messages by thread route.
    """
    thread_id = app.db.post_thread("user", "test")
    app.db.post_message(thread_id, "content", "user")
    app.db.post_message(thread_id, "content2", "assistant")
    response = client.get(f"/threads/{thread_id}/messages")
    assert response.json
    data = [
        {"content": item["content"], "role": item["role"]} for item in response.json
    ]
    assert response.status_code == 200
    assert data == [
        {"content": "content", "role": "user"},
        {"content": "content2", "role": "assistant"},
    ]


def test_delete_messages_more_recent(app: App, client: FlaskClient) -> None:
    """
    Test the delete messages more recent route.
    """
    # Setup messages
    thread_id = app.db.post_thread("user", "chatbot")
    alt_thread = app.db.post_thread("user2", "chatbot2")
    app.db.post_message(thread_id, "test message", "user")
    time.sleep(1)  # Ensure the messages have different timestamps
    app.db.post_message(thread_id, "test message2", "assistant")
    time.sleep(1)
    app.db.post_message(thread_id, "test message3", "user")
    app.db.post_message(alt_thread, "alt message", "user")

    # Check that messages are deleted correctly
    response = client.delete("/messages/2")
    assert response.status_code == 200
    messages = app.db.get_messages_by_thread(thread_id)
    assert len(messages) == 1
    assert messages[0]["content"] == "test message"


def test_get_response_now(app: App, client: FlaskClient) -> None:
    """
    Test the get response now route.
    """
    # Setup messages
    thread_id = app.db.post_thread("user", "test")
    app.db.post_message(thread_id, "test message", "user")
    app.db.post_message(
        thread_id,
        "test message2",
        "assistant",
        datetime.now(timezone.utc) + timedelta(minutes=5),
    )

    # Check that the response is applied
    response = client.get(f"/threads/{thread_id}/messages/new")
    assert response.status_code == 200
    time.sleep(1)
    messages = app.db.get_messages_by_thread(thread_id)
    assert messages[-1]["timestamp"] < datetime.now(timezone.utc)


def test_get_response_now_new(app: App, client: FlaskClient) -> None:
    """
    Test the get response now route.
    """
    # Setup messages
    thread_id = app.db.post_thread("user", "test")
    app.db.post_message(thread_id, "test message", "user", datetime.now(timezone.utc))
    time.sleep(2)

    # Check that a new response is generated if there is no scheduled message
    response = client.get(f"/threads/{thread_id}/messages/new")
    assert response.status_code == 200
    time.sleep(2)
    messages = app.db.get_messages_by_thread(thread_id)
    assert len(messages) == 2
    assert messages[-1]["content"] == "Mock response"
    assert messages[-1]["timestamp"] < datetime.now(timezone.utc)


def test_get_events_by_character(app: App, client: FlaskClient) -> None:
    """
    Test the get events by character route.
    """
    app.db.post_event("test", "event", "test")
    app.db.post_event("test", "event", "test2")
    app.db.post_event("test", "thought", "test")
    response = client.get("/events/test")
    assert response.status_code == 200
    assert response.json[0]["id"] == 1
    assert response.json[0]["content"] == "test"
    assert response.json[1]["id"] == 2
    assert response.json[1]["content"] == "test2"


def test_get_posts_by_character(app: App, client: FlaskClient) -> None:
    """
    Test the get posts by character route.
    """
    app.db.post_social_media_post(
        "chatbot", "test post", "test,prompt,", "test caption"
    )
    app.db.post_social_media_post(
        "chatbot", "test post2", "test,prompt,", "test caption2"
    )
    app.db.post_social_media_post(
        "chatbot", "test post3", "test,prompt,", "test caption3"
    )
    app.db.post_social_media_post(
        "chatbot2", "test post", "test,prompt,", "test caption"
    )
    response = client.get("/posts/chatbot")
    assert response.status_code == 200
    assert len(response.json) == 3
    assert response.json[0]["description"] == "test post"
    assert response.json[1]["description"] == "test post2"
    assert response.json[2]["description"] == "test post3"
