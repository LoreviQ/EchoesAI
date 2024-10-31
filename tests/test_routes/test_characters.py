"""
This file contains the tests for the routes/characters.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import


from unittest.mock import MagicMock, patch

from flask.testing import FlaskClient

import database as db

from .fixtures import app, client


@patch("database.insert_character")
def test_post_character(mock_insert_character: MagicMock, client: FlaskClient) -> None:
    """
    Test the post character route.
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
    mock_insert_character.assert_called_once_with(character_payload)


def test_post_character_missing_required_fields(client: FlaskClient) -> None:
    """
    Test the npost character route with missing required fields.
    """
    character_payload = {
        "name": "Test Character",
        "description": "Test description",
    }
    response = client.post("/v1/characters", json=character_payload)
    assert response.status_code == 400
    assert response.data == b"Missing required fields"


@patch("database.select_character")
def test_get_character(mock_select_character: MagicMock, client: FlaskClient) -> None:
    """
    Test the get character by Path route.
    """
    char_1 = db.Character(id=1, name="Test Character", path_name="test_character")
    mock_select_character.return_value = char_1
    response = client.get("/v1/characters/test_character")
    assert response.status_code == 200
    assert response.json
    assert response.json["id"] == char_1["id"]
    assert response.json["name"] == char_1["name"]
    assert mock_select_character.called_once_with(char_1["path_name"])


@patch("database.select_character")
def test_get_character_fail(
    mock_select_character: MagicMock, client: FlaskClient
) -> None:
    """
    Test the get character by ID route.
    """
    mock_select_character.side_effect = ValueError
    response = client.get("/v1/characters/not_a_character")
    assert response.status_code == 404
    assert response.data == b"character not found"
    assert mock_select_character.called_once_with("not_a_character")


@patch("database.select_characters")
def test_get_characters(mock_select_characters: MagicMock, client: FlaskClient) -> None:
    """
    Test the get characters route without a query.
    """
    char_1 = db.Character(id=1, name="Test Character 1", path_name="test_character_1")
    char_2 = db.Character(id=2, name="Test Character 2", path_name="test_character_2")
    mock_select_characters.return_value = [
        char_1,
        char_2,
    ]
    response = client.get("/v1/characters?")
    assert response.status_code == 200
    assert response.json
    assert response.json[0]["id"] == char_1["id"]
    assert response.json[0]["name"] == char_1["name"]
    assert response.json[1]["id"] == char_2["id"]
    assert response.json[1]["name"] == char_2["name"]
    assert mock_select_characters.called_once_with({})


@patch("database.select_characters")
def test_get_characters_query(
    mock_select_characters: MagicMock, client: FlaskClient
) -> None:
    """
    Test the get characters route with a query.
    """
    char = db.Character(id=1, name="TestCharacter1", path_name="test_character_1")
    mock_select_characters.return_value = [
        char,
    ]
    query = "?name=TestCharacter1"
    response = client.get(f"/v1/characters{query}")
    assert response.status_code == 200
    assert response.json
    assert len(response.json) == 1
    assert response.json[0]["id"] == char["id"]
    assert response.json[0]["name"] == char["name"]
    assert mock_select_characters.called_once_with({"name": char["name"]})


@patch("database.select_characters")
def test_get_characters_query_no_matching(
    mock_select_characters: MagicMock, client: FlaskClient
) -> None:
    """
    Test the get characters route with a query that doesn't match any characters.
    """
    mock_select_characters.return_value = []
    query = "?name=not_a_character"
    response = client.get("/v1/characters" + query)
    assert response.status_code == 200
    assert not response.json
    assert mock_select_characters.called_once_with({"name": "not_a_character"})


@patch("database.select_character")
@patch("database.select_posts")
def test_get_posts_by_character(
    mock_select_posts: MagicMock, mock_select_character: MagicMock, client: FlaskClient
) -> None:
    """
    Test the get characters posts.
    """
    post_1 = db.Post(id=1, content="Test content 1")
    post_2 = db.Post(id=2, content="Test content 2")
    mock_select_character.return_value = db.Character(
        id=1, name="Test Character", path_name="test_character"
    )
    mock_select_posts.return_value = [post_1, post_2]
    response = client.get("/v1/characters/test_character/posts")
    assert response.status_code == 200
    assert response.json
    assert response.json[0]["id"] == post_1["id"]
    assert response.json[1]["id"] == post_2["id"]
    assert mock_select_character.called_once_with("test_character")
    assert mock_select_posts.called_once_with(db.Post(char_id=1))


@patch("database.select_character")
@patch("database.select_posts")
def test_get_posts_by_character_no_posts(
    mock_select_posts: MagicMock, mock_select_character: MagicMock, client: FlaskClient
) -> None:
    """
    Test the get posts by character route with no posts.
    """
    char = db.Character(id=1, name="Test Character", path_name="test_character")
    mock_select_character.return_value = char
    mock_select_posts.return_value = []
    response = client.get("/v1/characters/test_character/posts")
    assert response.status_code == 200
    assert response.json == []
    assert mock_select_character.called_once_with("test_character")
    assert mock_select_posts.called_once_with(db.Post(char_id=char["id"]))


@patch("database.select_character")
def test_get_posts_by_character_invalid_character(
    mock_select_character: MagicMock, client: FlaskClient
) -> None:
    """
    Test the get posts by character route with an invalid character.
    """
    mock_select_character.side_effect = ValueError
    response = client.get("/v1/characters/not_a_character/posts")
    assert response.status_code == 404
    assert response.data == b"character not found"


@patch("database.select_character")
@patch("database.select_events")
def test_get_events_by_character(
    mock_select_events: MagicMock, mock_select_character: MagicMock, client: FlaskClient
) -> None:
    """
    Test the get characters events.
    """
    event_1 = db.Event(id=1, char_id=1, type="event", content="Test content 1")
    event_2 = db.Event(id=2, char_id=1, type="event", content="Test content 2")
    char = db.Character(id=1, name="Test Character", path_name="test_character")
    mock_select_character.return_value = char
    mock_select_events.return_value = [event_1, event_2]
    response = client.get(f"/v1/characters/{char['path_name']}/events")
    assert response.status_code == 200
    assert response.json
    assert response.json[0]["id"] == event_1["id"]
    assert response.json[1]["id"] == event_2["id"]
