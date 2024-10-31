"""
This file contains the tests for the routes/main.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

import os
from datetime import datetime, timezone
from typing import Generator, Tuple

import pytest
from flask.testing import FlaskClient

import database as db
from app import App
from tests.test_database.test_main import test_db

from .fixtures import app, client


def test_ready(client: FlaskClient) -> None:
    """
    Test the readiness route.
    """
    response = client.get("/v1/readiness")
    assert response.status_code == 200


def test_detached_false(app: App, client: FlaskClient) -> None:
    """
    Test the detached route.
    """
    response = client.get("/v1/detached")
    assert response.status_code == 200  #
    assert response.data == b"False"


def test_detached_true() -> None:
    """
    Test the detached route with a detached app.
    """
    app = App(mocked=True, detached=True)
    with app.app.test_client() as client:
        response = client.get("/v1/detached")
        assert response.status_code == 200
        assert response.data == b"True"
