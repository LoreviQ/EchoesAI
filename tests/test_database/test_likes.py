"""Tests for the likes module in the database package."""

# pylint: disable=redefined-outer-name unused-argument unused-import


from typing import List

import database as db

from .fixtures import character, characters, comments, post, posts
from .test_main import test_db


def test_insert_like(post: db.Post) -> None:
    """Test the insert_comment function."""
    like = db.Like(
        user_id=1,
        content_liked="post",
        content_id=post["id"],
    )
    result = db.insert_like(like)
    assert result == 1


def test_select_likes(comments: List[db.Comment], posts: List[db.Post]) -> None:
    """Test the select_likes function."""
    like = db.Like(
        user_id=1,
        content_liked="post",
        content_id=posts[0]["id"],
    )
    like2 = db.Like(
        user_id=2,
        content_liked="post",
        content_id=posts[1]["id"],
    )
    like3 = db.Like(
        user_id=1,
        content_liked="comment",
        content_id=comments[0]["id"],
    )
    db.insert_like(like)
    db.insert_like(like2)
    db.insert_like(like3)
    result = db.select_likes()
    assert len(result) == 3
    assert result[0]["user_id"] == 1
    assert result[0]["content_liked"] == "post"
    assert result[0]["content_id"] == posts[0]["id"]
    assert result[1]["user_id"] == 2
    assert result[1]["content_liked"] == "post"
    assert result[1]["content_id"] == posts[1]["id"]
    assert result[2]["user_id"] == 1
    assert result[2]["content_liked"] == "comment"
    assert result[2]["content_id"] == comments[0]["id"]


def test_count_likes(comments: List[db.Comment], posts: List[db.Post]) -> None:
    """Test the count_likes function."""
    like = db.Like(
        user_id=1,
        content_liked="post",
        content_id=posts[0]["id"],
    )
    like2 = db.Like(
        user_id=2,
        content_liked="post",
        content_id=posts[0]["id"],
    )
    like3 = db.Like(
        user_id=1,
        content_liked="comment",
        content_id=comments[0]["id"],
    )
    db.insert_like(like)
    db.insert_like(like2)
    db.insert_like(like3)
    result = db.count_likes("post", posts[0]["id"])
    assert result == 2
    result = db.count_likes("comment", comments[0]["id"])
    assert result == 1


def test_has_user_liked(post: db.Post) -> None:
    """Test the has_user_liked function."""
    like = db.Like(
        user_id=1,
        content_liked="post",
        content_id=post["id"],
    )
    db.insert_like(like)
    result = db.has_user_liked(1, "post", post["id"])
    assert result is True
    result = db.has_user_liked(2, "post", post["id"])
    assert result is False


def test_delete_like(post: db.Post) -> None:
    """Test the delete_like function."""
    like = db.Like(
        user_id=1,
        content_liked="post",
        content_id=post["id"],
    )
    like_id = db.insert_like(like)
    db.delete_like(like_id)
    result = db.select_likes()
    assert not result
