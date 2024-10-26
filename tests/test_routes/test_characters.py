"""
This file contains the tests for the routes/characters.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import


from flask.testing import FlaskClient

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
    response = client.post("/v1/characters", json=character_payload)
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
    response = client.post("/v1/characters", json=character_payload)
    assert response.status_code == 400
    assert response.data == b"Missing required fields"


def test_get_character(client: FlaskClient, char_1: db.Character) -> None:
    """
    Test the get character by ID route.
    """
    response = client.get(f"/v1/characters/{char_1['id']}")
    assert response.status_code == 200
    assert response.json
    assert response.json["id"] == char_1["id"]
    assert response.json["name"] == char_1["name"]


def test_get_character_fail(client: FlaskClient) -> None:
    """
    Test the get character by ID route.
    """
    response = client.get(f"/v1/characters/{50}")
    assert response.status_code == 404
    assert response.data == b"character not found"


def test_get_characters(
    client: FlaskClient, char_1: db.Character, char_2: db.Character
) -> None:
    """
    Test the get characters route without a query.
    """
    response = client.get("/v1/characters?")
    assert response.status_code == 200
    assert response.json
    assert response.json[0]["id"] == char_1["id"]
    assert response.json[0]["name"] == char_1["name"]
    assert response.json[1]["id"] == char_2["id"]
    assert response.json[1]["name"] == char_2["name"]


def test_get_characters_query(
    client: FlaskClient, char_1: db.Character, char_2: db.Character
) -> None:
    """
    Test the get characters route with a query.
    """
    query = f"?name={char_1['name']}"
    response = client.get("/v1/characters" + query)
    assert response.status_code == 200
    assert response.json
    assert len(response.json) == 1
    assert response.json[0]["id"] == char_1["id"]
    assert response.json[0]["name"] == char_1["name"]


def test_get_characters_query_no_matching(
    client: FlaskClient, char_1: db.Character, char_2: db.Character
) -> None:
    """
    Test the get characters route with a query that doesn't match any characters.
    """
    query = "?name=not_a_character"
    response = client.get("/v1/characters" + query)
    assert response.status_code == 200
    assert len(response.json) == 0
