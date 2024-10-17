"""
This file contains the tests for the app.py file.
"""

# pylint: disable=redefined-outer-name

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
