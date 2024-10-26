"""
This file contains the tests for the routes/characters.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import


from flask.testing import FlaskClient

import auth
import database as db
from tests.test_app import app, client
from tests.test_database.test_characters import char_1, char_2
from tests.test_database.test_main import db_init


def test_new_character(client: FlaskClient) -> None:
    """
    Test the new character route.
    """
    character_payload = {
        "name": "Test Character",
        "path_name": "test_character",
        "description": "Test description",
    }
    response = client.post("/characters/new", json=character_payload)
    assert response.status_code == 200
    assert response.data
    char_path = response.data.decode("utf-8")
    assert char_path == character_payload["path_name"]


def test_new_character_missing_required_fields(client: FlaskClient) -> None:
    """
    Test the new character route with missing required fields.
    """
    character_payload = {
        "name": "Test Character",
        "description": "Test description",
    }
    response = client.post("/characters/new", json=character_payload)
    assert response.status_code == 400
    assert response.data == b"Missing required fields"


def test_get_character(client: FlaskClient, char_1: db.Character) -> None:
    """
    Test the get character by ID route.
    """
    response = client.get(f"/characters/id/{char_1['id']}")
    assert response.status_code == 200
    assert response.json
    assert response.json["id"] == char_1["id"]
    assert response.json["name"] == char_1["name"]


def test_get_character_fail(client: FlaskClient) -> None:
    """
    Test the get character by ID route.
    """
    response = client.get(f"/characters/id/{50}")
    assert response.status_code == 404
    assert response.data == b"character not found"


def test_get_character_by_path(client: FlaskClient, char_2: db.Character) -> None:
    """
    Test the get character by path route.
    """
    response = client.get(f"/characters/path/{char_2['path_name']}")
    assert response.status_code == 200
    assert response.json
    assert response.json["id"] == char_2["id"]
    assert response.json["name"] == char_2["name"]
    assert response.json["path_name"] == char_2["path_name"]


def test_get_character_by_path_fail(client: FlaskClient) -> None:
    """
    Test the get character by path route.
    """
    response = client.get("/characters/path/does_not_exist")
    assert response.status_code == 404
    assert response.data == b"character not found"
