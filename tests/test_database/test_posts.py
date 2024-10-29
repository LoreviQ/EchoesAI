"""
This file contains the tests for the database/posts.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

from typing import Generator

import pytest

import database as db
from tests.test_database.test_characters import char_1, char_2
from tests.test_database.test_main import db_init


@pytest.fixture
def post_1(char_1: db.Character) -> Generator[db.Post, None, None]:
    """
    Creates a post to be used in testing.
    """
    post = db.Post(
        char_id=char_1["id"],
        description="test description",
        image_post=True,
        prompt="test prompt",
        caption="test caption",
    )
    post["id"] = db.posts.insert_social_media_post(post)
    yield post


@pytest.fixture
def post_2(char_1: db.Character) -> Generator[db.Post, None, None]:
    """
    Creates a post distinct from post_1 to be used in testing.
    """
    post = db.Post(
        char_id=char_1["id"],
        description="test description 2",
        image_post=False,
        prompt="",
        caption="",
    )
    post["id"] = db.posts.insert_social_media_post(post)
    yield post


def test_insert_social_media_post(db_init: str, char_1: db.Character) -> None:
    """
    Test the insert_social_media_post function.
    """
    post = db.Post(
        char_id=char_1["id"],
        description="test description",
        image_post=True,
        prompt="test prompt",
        caption="test caption",
    )
    post_id = db.posts.insert_social_media_post(post)
    assert post_id == 1


def test_select_posts(db_init: str, char_1: db.Character, char_2: db.Character) -> None:
    """
    Test the select_posts function.
    """
    assert char_1["id"]
    post1 = db.Post(
        char_id=char_1["id"],
        description="test description",
        image_post=True,
        prompt="test prompt",
        caption="test caption",
    )
    post2 = db.Post(
        char_id=char_1["id"],
        description="test description 2",
        image_post=True,
        prompt="test prompt 2",
        caption="test caption 2",
    )
    post3 = db.Post(
        char_id=char_2["id"],
        description="test description 3",
        image_post=True,
        prompt="test prompt 3",
        caption="test caption 3",
    )
    post1_id = db.posts.insert_social_media_post(post1)
    post2_id = db.posts.insert_social_media_post(post2)
    post3_id = db.posts.insert_social_media_post(post3)
    posts = db.posts.select_posts()
    assert len(posts) == 3
    assert posts[0]["id"] == post1_id
    assert posts[1]["id"] == post2_id
    assert posts[2]["id"] == post3_id


def test_select_posts_with_query(
    db_init: str, char_1: db.Character, char_2: db.Character
) -> None:
    """
    Test the select_posts function.
    """
    assert char_1["id"]
    post1 = db.Post(
        char_id=char_1["id"],
        description="test description",
        image_post=True,
        prompt="test prompt",
        caption="test caption",
    )
    post2 = db.Post(
        char_id=char_1["id"],
        description="test description 2",
        image_post=True,
        prompt="test prompt 2",
        caption="test caption 2",
    )
    post3 = db.Post(
        char_id=char_2["id"],
        description="test description 3",
        image_post=True,
        prompt="test prompt 3",
        caption="test caption 3",
    )
    post1_id = db.posts.insert_social_media_post(post1)
    post2_id = db.posts.insert_social_media_post(post2)
    db.posts.insert_social_media_post(post3)
    post_query = db.Post(char_id=char_1["id"])
    posts = db.posts.select_posts(post_query)
    assert len(posts) == 2
    assert posts[0]["id"] == post1_id
    assert posts[1]["id"] == post2_id


def test_add_image_path_to_post(db_init: str, char_1: db.Character) -> None:
    """
    Test the add_image_path_to_post function.
    """
    assert char_1["id"]
    post = db.Post(
        char_id=char_1["id"],
        description="test description",
        image_post=True,
        prompt="test prompt",
        caption="test caption",
    )
    post_id = db.posts.insert_social_media_post(post)
    db.posts.update_post_with_image_path(post_id, "test_image_path")
    post = db.posts.select_posts(db.Post(id=post_id))[0]
    assert post["image_path"] == "test_image_path"
