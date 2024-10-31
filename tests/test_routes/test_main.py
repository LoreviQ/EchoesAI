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
from tests.test_app import app, client
from tests.test_database.test_main import test_db


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
    response = client.get("/v1/readiness")
    assert response.status_code == 200


def test_get_image(client: FlaskClient, expected_image: Tuple[str, bytes]) -> None:
    """
    Test the get image route.
    """
    response = client.get(f"/v1/{expected_image[0]}")
    assert response.status_code == 200
    assert response.data == expected_image[1]


def test_get_image_with_invalid_path(client: FlaskClient) -> None:
    """
    Test the get image route with an invalid path.
    """
    response = client.get("/v1/images/../pwd.txt")
    assert response.status_code == 404


def test_convert_dt_ts() -> None:
    """
    Test the convert_dt_ts function.
    """

    dt = datetime(2021, 1, 1, 0, 0, 0)
    assert db.convert_dt_ts(dt) == "2021-01-01 00:00:00"

    with pytest.raises(ValueError):
        db.convert_dt_ts(None)


def test_convert_ts_dt() -> None:
    """
    Test the convert_ts_dt function.
    """

    ts = "2024-10-26 22:47:11.580972+00:00"
    assert db.convert_ts_dt(ts) == datetime(
        2024, 10, 26, 22, 47, 11, tzinfo=timezone.utc
    )

    with pytest.raises(ValueError):
        db.convert_ts_dt(None)


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
