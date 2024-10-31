"""
This file contains the tests for the routes/posts.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

from flask.testing import FlaskClient

import database_old as db
from not_t.test_app import app, client
from not_t.test_database_old.test_characters import char_1
from not_t.test_database_old.test_main import db_init
from not_t.test_database_old.test_posts import post_1, post_2


def test_get_posts(client: FlaskClient, post_1: db.Post, post_2: db.Post) -> None:
    """
    Test the get posts route without a query.
    """
    response = client.get("/v1/posts")
    assert response.status_code == 200
    assert response.json
    assert response.json[0]["id"] == post_1["id"]
    assert response.json[1]["id"] == post_2["id"]


def test_get_posts_no_posts(client: FlaskClient) -> None:
    """
    Test the get posts  route with no posts.
    """
    response = client.get("/v1/posts")
    assert response.status_code == 200
    assert response.json == []


def test_get_posts_with_query(
    client: FlaskClient, char_1: db.Character, post_1: db.Post, post_2: db.Post
) -> None:
    """
    Test the get posts route with a query specifying a character.
    """
    query = f"?char_path={char_1['path_name']}"
    response = client.get(f"/v1/posts{query}")
    assert response.status_code == 200
    assert response.json
    assert response.json[0]["id"] == post_1["id"]
    assert response.json[1]["id"] == post_2["id"]
