"""
This file contains the tests for the routes/main.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

import os
from typing import Generator, Tuple

import pytest
from flask.testing import FlaskClient

from tests.test_app import app, client
from tests.test_database.test_main import db_init


@pytest.fixture
def expected_image() -> Generator[Tuple[str, bytes], None, None]:
    """Yields an image and its path."""
    img_path = os.path.join("images", "test", "profile.jpg")
    full_path = os.path.join("static", img_path)
    with open(full_path, "rb") as img:
        yield img_path, img.read()


def test_ready(client: FlaskClient) -> None:
    """
    Test the readiness route.
    """
    response = client.get("/readiness")
    assert response.status_code == 200


def test_get_image(client: FlaskClient, expected_image: Tuple[str, bytes]) -> None:
    """
    Test the get image route.
    """
    response = client.get(expected_image[0])
    assert response.status_code == 200
    assert response.data == expected_image[1]


def test_get_image_with_invalid_path(client: FlaskClient) -> None:
    """
    Test the get image route with an invalid path.
    """
    response = client.get("/images/../pwd.txt")
    assert response.status_code == 404
