"""This file contains the tests for the app.py file."""

# pylint: disable=redefined-outer-name unused-argument unused-import


import os
from multiprocessing import Value
from typing import Generator, Tuple

import pytest
from flask.testing import FlaskClient

from app import App
from chatbot import new_model
from tests.test_database.test_main import test_db

# Shared counter for port numbers
port_counter = Value("i", 5000)


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> Generator[App, None, None]:
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


@pytest.fixture
def expected_image() -> Generator[Tuple[str, bytes], None, None]:
    """Yields an image and its path."""
    img_path = os.path.join("images", "test", "profile.jpg")
    full_path = os.path.join("static", img_path)
    with open(full_path, "rb") as img:
        yield img_path, img.read()
