"""Tests for the posts module in the database package."""

# pylint: disable=redefined-outer-name unused-argument unused-import


from typing import List

import database as db

from .fixtures import character, characters
from .test_main import test_db


def test_insert_post(character: db.Character) -> None:
    """Test the insert_post function."""
    post = db.Post(
        char_id=character["id"],
        content="test caption",
        image_post=True,
        prompt="test prompt",
        image_description="test description",
    )
    result = db.insert_post(post)
    assert result == 1


def test_select_post(character: db.Character) -> None:
    """Test the select_post function."""
    post = db.Post(
        char_id=character["id"],
        content="test caption",
        image_post=True,
        prompt="test prompt",
        image_description="test description",
    )
    post_id = db.insert_post(post)
    result = db.select_post(post_id)
    assert result["content"] == "test caption"
    assert result["image_post"] is True
    assert result["prompt"] == "test prompt"


def test_update_post_with_image_path(character: db.Character) -> None:
    """Test the update_post_with_image_path function."""
    post = db.Post(
        char_id=character["id"],
        content="test caption",
        image_post=True,
        prompt="test prompt",
        image_description="test description",
    )
    post_id = db.insert_post(post)
    db.update_post_with_image_path(post_id, "test_image_path")
    result = db.select_post(post_id)
    assert result["image_path"] == "test_image_path"


def test_select_posts_without_query(characters: List[db.Character]) -> None:
    """Test the select_posts function without a query."""
    post = db.Post(
        char_id=characters[0]["id"],
        content="test caption",
        image_post=True,
        prompt="test prompt",
        image_description="test description",
    )
    post2 = db.Post(
        char_id=characters[1]["id"],
        content="test caption 2",
        image_post=True,
        prompt="test prompt 2",
        image_description="test description 2",
    )
    post1_id = db.insert_post(post)
    post2_id = db.insert_post(post2)
    result = db.select_posts()
    assert len(result) == 2
    assert result[0]["id"] == post1_id
    assert result[1]["id"] == post2_id


def test_select_posts_with_query(characters: List[db.Character]) -> None:
    """Test the select_posts function with a query."""
    post = db.Post(
        char_id=characters[0]["id"],
        content="test caption",
        image_post=True,
        prompt="test prompt",
        image_description="test description",
    )
    post2 = db.Post(
        char_id=characters[1]["id"],
        content="test caption 2",
        image_post=True,
        prompt="test prompt 2",
        image_description="test description 2",
    )
    post3 = db.Post(
        char_id=characters[0]["id"],
        content="test caption 3",
        image_post=True,
        prompt="test prompt 3",
        image_description="test description 3",
    )
    post1_id = db.insert_post(post)
    db.insert_post(post2)
    post3_id = db.insert_post(post3)

    post_query = db.Post(char_id=characters[0]["id"])
    result = db.select_posts(post_query)
    assert len(result) == 2
    assert result[0]["id"] == post1_id
    assert result[1]["id"] == post3_id
