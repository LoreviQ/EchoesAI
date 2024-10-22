"""
This file contains the tests for the database/threads.py file.
"""

import os
import time
from typing import Generator

import pytest

import database as db

# pylint: disable=redefined-outer-name unused-argument unused-import


@pytest.fixture
def chars(monkeypatch) -> Generator[str, None, None]:
    """
    Create a DB object for testing and teardown after testing.
    """
    test_name = os.environ.get("PYTEST_CURRENT_TEST")
    if test_name is None:
        test_name = "unknown"
    else:
        test_name = test_name.split(":")[-1].split(" ")[0]
    db_path = f"test_database_{test_name}.db"
    monkeypatch.setattr("database.main.DB_PATH", db_path)
    db.main.create_db()
    character_1 = db.characters.Character(name="test character")
    character_1["id"] = db.characters.insert_character(character_1)
    character_2 = db.characters.Character(name="test character 2")
    character_2["id"] = db.characters.insert_character(character_2)
    yield character_1, character_2
    os.remove(db_path)


def test_insert_social_media_post(chars) -> None:
    """
    Test the insert_social_media_post function.
    """
    post = db.posts.Post(
        character=chars[0]["id"],
        description="test description",
        prompt="test prompt",
        caption="test caption",
    )
    post_id = db.posts.insert_social_media_post(post)
    assert post_id == 1


def test_get_posts_by_character(chars) -> None:
    """
    Test the get_posts_by_character function.
    """
    post1 = db.posts.Post(
        character=chars[0]["id"],
        description="test description",
        prompt="test prompt",
        caption="test caption",
    )
    post2 = db.posts.Post(
        character=chars[0]["id"],
        description="test description 2",
        prompt="test prompt 2",
        caption="test caption 2",
    )
    post3 = db.posts.Post(
        character=chars[1]["id"],
        description="test description 3",
        prompt="test prompt 3",
        caption="test caption 3",
    )
    post1_id = db.posts.insert_social_media_post(post1)
    post2_id = db.posts.insert_social_media_post(post2)
    db.posts.insert_social_media_post(post3)
    posts = db.posts.get_posts_by_character(chars[0]["id"])
    assert len(posts) == 2
    assert posts[0]["id"] == post1_id
    assert posts[1]["id"] == post2_id


def test_add_image_path_to_post(chars) -> None:
    """
    Test the add_image_path_to_post function.
    """
    post = db.posts.Post(
        character=chars[0]["id"],
        description="test description",
        prompt="test prompt",
        caption="test caption",
    )
    post_id = db.posts.insert_social_media_post(post)
    db.posts.add_image_path_to_post(post_id, "test_image_path")
    post = db.posts.get_posts_by_character(chars[0]["id"])[0]
    assert post["image_path"] == "test_image_path"
