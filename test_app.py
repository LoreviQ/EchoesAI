"""
This file contains the tests for the app.py file.
"""

# pylint: disable=redefined-outer-name

import json
import os
from multiprocessing import Value
from typing import Generator

import pytest
from flask.testing import FlaskClient

from app import App

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
    app = App(db_path=db_path, port=port)
    yield app
    app.db.conn.close()
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


def test_new_chatbot(app: App, client: FlaskClient) -> None:
    """
    Test the new chatbot route.
    """
    thread_id = app.db.post_thread("user", "test")
    response = client.post(f"/chatbot/{thread_id}")
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
        {"id": 1, "character": "test"},
        {"id": 2, "character": "test2"},
    ]


def test_get_messages_by_thread(app: App, client: FlaskClient) -> None:
    """
    Test the get messages by thread route.
    """
    thread_id = app.db.post_thread("user", "test")
    app.db.post_message(thread_id, "content", "user")
    app.db.post_message(thread_id, "content2", "assistant")
    response = client.get(f"/thread/{thread_id}/messages")
    assert response.json
    data = [
        {"content": item["content"], "role": item["role"]} for item in response.json
    ]
    assert response.status_code == 200
    assert data == [
        {"content": "content", "role": "user"},
        {"content": "content2", "role": "assistant"},
    ]
