"""
This file contains the tests for the routes/posts.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

from unittest.mock import MagicMock, patch

from flask.testing import FlaskClient

import database as db

from .fixtures import app, client


@patch("database.select_posts")
@patch("database.select_character")
def test_get_posts_with_query(
    mock_select_character: MagicMock, mock_select_posts: MagicMock, client: FlaskClient
) -> None:
    """
    Test the get posts route with a query specifying a character.
    """
    char = db.Character(id=1, path_name="test_character")
    mock_select_character.return_value = char
    post_1 = db.Post(id=1, char_id=1, content="Test post 1")
    post_2 = db.Post(id=2, char_id=1, content="Test post 2")
    mock_select_posts.return_value = [post_1, post_2]
    query = "?char_path=test_character"
    response = client.get(f"/v1/posts{query}")
    assert response.status_code == 200
    assert response.json
    assert response.json[0]["id"] == post_1["id"]
    assert response.json[1]["id"] == post_2["id"]
    assert mock_select_posts.called_once_with(db.Post(char_id=1))
