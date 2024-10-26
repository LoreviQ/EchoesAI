"""
This file contains the tests for the routes/main.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

import urllib.parse

from flask.testing import FlaskClient

import database as db
from tests.test_app import app, client
from tests.test_database.test_characters import char_1, char_2
from tests.test_database.test_main import db_init
from tests.test_database.test_threads import thread_1, thread_2


def test_new_thread(client: FlaskClient, char_1: db.Character) -> None:
    """
    Test the new thread route.
    """
    response = client.post(
        "/threads/new",
        json={"username": "user", "character": char_1["id"]},
    )
    assert response.status_code == 200
    assert response.data == b"1"


def test_get_threads_by_user(
    client: FlaskClient, char_1: db.Character, thread_1: db.Thread
) -> None:
    """
    Test the get threads by user route.
    """
    username_url = urllib.parse.quote(char_1["name"])
    response = client.get(f"/threads/{username_url}")
    assert response.status_code == 200
    assert response.json
    assert response.json[0]["id"] == thread_1["id"]
