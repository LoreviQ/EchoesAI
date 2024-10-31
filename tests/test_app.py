"""This file contains the tests for the app.py file."""

# pylint: disable=redefined-outer-name unused-argument unused-import


from multiprocessing import Value
from typing import Generator

import pytest
from flask.testing import FlaskClient

from app import App
from chatbot import new_model
from tests.test_database.test_main import test_db

# Shared counter for port numbers
port_counter = Value("i", 5000)


@pytest.fixture
def app(test_db: str, monkeypatch: pytest.MonkeyPatch) -> Generator[App, None, None]:
    """
    Create an App object for testing and teardown after testing.
    """
    with port_counter.get_lock():
        monkeypatch.setenv(
            "PORT",
            f"{port_counter.value}",
        )
        port_counter.value += 1
    app = App(mocked=True)
    yield app


@pytest.fixture
def client(app: App) -> Generator[FlaskClient, None, None]:
    """
    Create a Flask test client for testing and teardown after testing.
    """
    with app.app.test_client() as client:
        yield client
