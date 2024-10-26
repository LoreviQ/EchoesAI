"""
This file contains the tests for the routes/events.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import


from tests.test_app import app, client
from tests.test_database.test_characters import char_1
from tests.test_database.test_events import event_1, event_2
from tests.test_database.test_main import db_init


def test_get_events_by_character(client, char_1, event_1, event_2):
    """
    Test the get events by character route.
    """
    response = client.get(f"/events/{char_1['path_name']}")
    assert response.status_code == 200
    assert response.json
    assert response.json[0]["id"] == event_1["id"]
    assert response.json[1]["id"] == event_2["id"]


def test_get_events_by_character_no_events(client, char_1):
    """
    Test the get events by character route.
    """
    response = client.get(f"/events/{char_1['path_name']}")
    assert response.status_code == 200
    assert response.json == []


def test_get_events_by_character_invalid_character(client):
    """
    Test the get events by character route.
    """
    response = client.get("/events/not_a_character")
    assert response.status_code == 404
    assert response.data == b"character not found"
