"""
This file contains the tests for the routes/events.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import


from unittest.mock import MagicMock, patch

from flask.testing import FlaskClient

import database as db

from .fixtures import app, client


@patch("database.select_events")
def test_get_events(mock_select_events: MagicMock, client: FlaskClient) -> None:
    """
    Test the get events route.
    """
    event_1 = db.Event(id=1, char_id=1, type="test", content="Test content")
    event_2 = db.Event(id=2, char_id=1, type="test", content="Test content")
    mock_select_events.return_value = [event_1, event_2]
    response = client.get("/v1/events")
    assert response.status_code == 200
    assert response.json
    assert response.json[0]["id"] == event_1["id"]
    assert response.json[1]["id"] == event_2["id"]
    assert mock_select_events.called_once_with(db.Event())


@patch("database.select_events")
@patch("database.select_character")
def test_get_events_with_query(
    mock_select_character: MagicMock, mock_select_events: MagicMock, client: FlaskClient
) -> None:
    """
    Test the get events route with a query specifying a characters path name.
    """
    char_1 = db.Character(id=1, name="Test Character", path_name="test_character")
    event_1 = db.Event(id=1, char_id=1, type="test", content="Test content")
    event_2 = db.Event(id=2, char_id=1, type="test", content="Test content")
    mock_select_events.return_value = [event_1, event_2]
    mock_select_character.return_value = char_1
    query = f"?char_path={char_1['path_name']}"
    response = client.get(f"/v1/events{query}")
    assert response.status_code == 200
    assert response.json
    assert response.json[0]["id"] == event_1["id"]
    assert response.json[1]["id"] == event_2["id"]
    assert mock_select_events.called_once_with(db.Event(char_id=char_1["id"]))
    assert mock_select_character.called_once_with(char_1["path_name"])


@patch("database.select_character")
def test_get_events_invalid_character(
    mock_select_character: MagicMock, client: FlaskClient
) -> None:
    """
    Test the get events by character route with an invalid character.
    """
    mock_select_character.side_effect = ValueError
    response = client.get("/v1/events?char_path=not_a_character")
    assert response.status_code == 200
    assert response.json == []
