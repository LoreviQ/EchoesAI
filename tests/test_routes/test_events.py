"""
This file contains the tests for the routes/events.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import


from tests.test_app import app, client
from tests.test_database.test_characters import char_1
from tests.test_database.test_events import event_1, event_2
from tests.test_database.test_main import db_init


def test_get_events(client, event_1, event_2):
    """
    Test the get events route.
    """
    response = client.get("/v1/events")
    assert response.status_code == 200
    assert response.json
    assert response.json[0]["id"] == event_1["id"]
    assert response.json[1]["id"] == event_2["id"]


def test_get_events_by_character(client, char_1, event_1, event_2):
    """
    Test the get events route with a query specifying a characters path name.
    """
    query = f"?char_path={char_1['path_name']}"
    response = client.get(f"/v1/events{query}")
    assert response.status_code == 200
    assert response.json
    assert response.json[0]["id"] == event_1["id"]
    assert response.json[1]["id"] == event_2["id"]


def test_get_events_no_events(client):
    """
    Test the get events route with no events.
    """
    response = client.get("/v1/events")
    assert response.status_code == 200
    assert response.json == []


def test_get_events_invalid_character(client):
    """
    Test the get events by character route with an invalid character.
    """
    response = client.get("/v1/events?char_path=not_a_character")
    assert response.status_code == 200
    assert response.json == []
