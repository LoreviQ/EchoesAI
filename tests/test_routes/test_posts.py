"""
This file contains the tests for the routes/posts.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import


from tests.test_app import app, client
from tests.test_database.test_characters import char_1
from tests.test_database.test_main import db_init
from tests.test_database.test_posts import post_1, post_2


def test_get_posts_by_character(client, char_1, post_1, post_2):
    """
    Test the get posts by character route.
    """
    response = client.get(f"/posts/{char_1['path_name']}")
    assert response.status_code == 200
    assert response.json
    assert response.json[0]["id"] == post_1["id"]
    assert response.json[1]["id"] == post_2["id"]


def test_get_posts_by_character_no_posts(client, char_1):
    """
    Test the get posts by character route with no posts.
    """
    response = client.get(f"/posts/{char_1['path_name']}")
    assert response.status_code == 200
    assert response.json == []


def test_get_posts_by_character_invalid_character(client):
    """
    Test the get posts by character route with an invalid character.
    """
    response = client.get("/posts/not_a_character")
    assert response.status_code == 404
    assert response.data == b"character not found"
