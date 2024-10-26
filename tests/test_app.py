"""
This file contains the tests for the app.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

import time
from datetime import datetime, timezone
from multiprocessing import Value
from typing import Generator, List

import pytest
from flask.testing import FlaskClient

import auth
import database as db
from app import App
from model import Model, ModelMocked
from tests.test_database.test_main import db_init

# Shared counter for port numbers
port_counter = Value("i", 5000)


@pytest.fixture
def app(db_init: str) -> Generator[App, None, None]:
    """
    Create an App object for testing and teardown after testing.
    """
    with port_counter.get_lock():
        port = port_counter.value
        port_counter.value += 1
    model = Model(ModelMocked("short"))
    app = App(model=model, port=port)
    yield app


@pytest.fixture
def client(app: App) -> Generator[FlaskClient, None, None]:
    """
    Create a Flask test client for testing and teardown after testing.
    """
    with app.app.test_client() as client:
        yield client
