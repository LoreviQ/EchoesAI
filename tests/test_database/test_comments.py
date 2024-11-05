"""Tests for the comments module in the database package."""

# pylint: disable=redefined-outer-name unused-argument unused-import


from typing import List

import database as db

from .fixtures import character, post, posts
from .test_main import test_db


def test_insert_comment(post: db.Post) -> None:
    """Test the insert_comment function."""
    comment = db.Comment(
        post_id=post["id"],
        char_id=post["char_id"],
        content="test comment",
    )
    result = db.insert_comment(comment)
    assert result == 1


def test_select_comments_without_query(post: db.Post) -> None:
    """Test the select_comments function without a query."""
    comment = db.Comment(
        post_id=post["id"],
        char_id=post["char_id"],
        content="test comment",
    )
    comment2 = db.Comment(
        post_id=post["id"],
        char_id=post["char_id"],
        content="test comment 2",
    )
    db.insert_comment(comment)
    db.insert_comment(comment2)
    result = db.select_comments()
    assert len(result) == 2
    assert result[0]["post_id"] == post["id"]
    assert result[0]["char_id"] == post["char_id"]
    assert result[0]["content"] == "test comment"
    assert result[1]["post_id"] == post["id"]
    assert result[1]["char_id"] == post["char_id"]
    assert result[1]["content"] == "test comment 2"


def test_select_comments_with_query(posts: List[db.Post]) -> None:
    """Test the select_comments function with a query."""
    comment = db.Comment(
        post_id=posts[0]["id"],
        char_id=posts[0]["char_id"],
        content="test comment",
    )
    comment2 = db.Comment(
        post_id=posts[0]["id"],
        char_id=posts[0]["char_id"],
        content="test comment 2",
    )
    comment3 = db.Comment(
        post_id=posts[1]["id"],
        char_id=posts[1]["char_id"],
        content="test comment 3",
    )
    comment1_id = db.insert_comment(comment)
    comment2_id = db.insert_comment(comment2)
    db.insert_comment(comment3)

    comment_query = db.Comment(post_id=posts[0]["id"])
    result = db.select_comments(comment_query)
    assert len(result) == 2
    assert result[0]["id"] == comment1_id
    assert result[0]["post_id"] == posts[0]["id"]
    assert result[0]["char_id"] == posts[0]["char_id"]
    assert result[0]["content"] == "test comment"
    assert result[1]["id"] == comment2_id
    assert result[1]["post_id"] == posts[0]["id"]
    assert result[1]["char_id"] == posts[0]["char_id"]
    assert result[1]["content"] == "test comment 2"


def test_select_comments_with_query_no_matching(post: db.Post) -> None:
    """Test the select_comments function with a query that doesn't match any comments."""
    comment = db.Comment(
        post_id=post["id"],
        char_id=post["char_id"],
        content="test comment",
    )
    comment2 = db.Comment(
        post_id=post["id"],
        char_id=post["char_id"],
        content="test comment 2",
    )
    db.insert_comment(comment)
    db.insert_comment(comment2)
    result = db.select_comments(db.Comment(post_id=999))
    assert not result
