"""
This file contains the tests for the routes/posts.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

from unittest.mock import MagicMock, patch

from flask.testing import FlaskClient

import database as db

from .fixtures import app, client


@patch("database.select_post")
@patch("database.select_comments")
@patch("database.select_character_by_id")
def test_get_posts_with_query(
    mock_select_character_by_id: MagicMock,
    mock_select_comments: MagicMock,
    mock_select_post: MagicMock,
    client: FlaskClient,
) -> None:
    """
    Test the get posts route with a query specifying a character.
    """
    post = db.Post(id=1, char_id=1, content="Test post")
    character = db.Character(id=1, path_name="test_character")
    comment_1 = db.Comment(
        id=1, post_id=post["id"], char_id=character["id"], content="Test comment 1"
    )
    comment_2 = db.Comment(
        id=2, post_id=post["id"], char_id=character["id"], content="Test comment 2"
    )
    mock_select_post.return_value = post
    mock_select_comments.return_value = [comment_1, comment_2]
    mock_select_character_by_id.return_value = character
    response = client.get(f"/v1/posts/{post['id']}/comments")
    assert response.status_code == 200
    assert response.json
    assert len(response.json) == 2
    assert response.json[0]["id"] == comment_1["id"]
    assert response.json[1]["id"] == comment_2["id"]
    assert mock_select_post.called_once_with(post["id"])
    assert mock_select_comments.called_once_with(db.Comment(post_id=post["id"]))
    assert mock_select_character_by_id.called_once_with(character["id"])
