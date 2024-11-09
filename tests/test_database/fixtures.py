"""Contains a numwea of database fixtures generating the required data before tests"""

# pylint: disable=redefined-outer-name unused-argument unused-import

from typing import Generator, List

import pytest

import database as db

from .test_main import test_db


@pytest.fixture
def character(test_db: None) -> Generator[db.Character, None, None]:
    """Creates a single character to be used in testing."""
    char_id = db.insert_character(
        db.Character(
            name="test character",
            path_name="test_character",
            img_gen=True,
            model="urn:air:sdxl:checkpoint:civitai:811067@907264",
            appearance="beep boop, robot, test, mechanical, cute, funny,",
            global_positive="best quality, amazing quality, very aesthetic,",
            global_negative="lowres, worst quality, low quality, bad anatomy, multiple views",
        )
    )
    yield db.select_character_by_id(char_id)


@pytest.fixture
def characters(test_db: None) -> Generator[List[db.Character], None, None]:
    """Creates a number of characters to be used in testing."""
    db.insert_character(
        db.Character(
            name="test character",
            path_name="test_character",
            img_gen=True,
            model="urn:air:sdxl:checkpoint:civitai:811067@907264",
            appearance="beep boop, robot, test, mechanical, cute, funny,",
            global_positive="best quality, amazing quality, very aesthetic,",
            global_negative="lowres, worst quality, low quality, bad anatomy, multiple views",
        )
    )
    db.insert_character(
        db.Character(
            name="test character 2",
            path_name="test_character_2",
            img_gen=False,
        )
    )
    db.insert_character(
        db.Character(
            name="test character 3",
            path_name="test_character_3",
            img_gen=False,
        )
    )
    yield db.select_characters()


@pytest.fixture
def user(test_db: None) -> Generator[db.User, None, None]:
    """Creates a single user to be used in testing."""
    user = db.User(
        username="test",
        password="test",
        email="test@test.com",
    )
    db.insert_user(user)
    yield db.select_user("test")


@pytest.fixture
def thread(user: db.User, character: db.Character) -> Generator[db.Thread, None, None]:
    """Creates a single thread to be used in testing."""
    thread = db.Thread(
        user_id=user["id"],
        char_id=character["id"],
    )
    thread_id = db.insert_thread(thread)
    yield db.select_thread(thread_id)


@pytest.fixture
def threads(
    user: db.User, characters: List[db.Character]
) -> Generator[List[db.Thread], None, None]:
    """Creates a number of threads to be used in testing."""
    thread = db.Thread(
        user_id=user["id"],
        char_id=characters[0]["id"],
    )
    thread2 = db.Thread(
        user_id=user["id"],
        char_id=characters[1]["id"],
    )
    thread3 = db.Thread(
        user_id=user["id"],
        char_id=characters[0]["id"],
    )
    db.insert_thread(thread)
    db.insert_thread(thread2)
    db.insert_thread(thread3)
    yield db.select_threads()


@pytest.fixture
def post(character: db.Character) -> Generator[db.Post, None, None]:
    """Creates a single post to be used in testing."""
    post = db.Post(
        char_id=character["id"],
        content="test caption",
        image_post=True,
        image_description="test description",
        prompt="test prompt",
    )
    post_id = db.posts.insert_post(post)
    yield db.select_post(post_id)


@pytest.fixture
def posts(character: db.Character) -> Generator[List[db.Post], None, None]:
    """Creates a number of posts to be used in testing."""
    post = db.Post(
        char_id=character["id"],
        content="test caption",
        image_post=True,
        image_description="test description",
        prompt="test prompt",
    )
    post2 = db.Post(
        char_id=character["id"],
        content="test caption 2",
        image_post=True,
        image_description="test description 2",
        prompt="test prompt 2",
    )
    post3 = db.Post(
        char_id=character["id"],
        content="test caption 3",
        image_post=True,
        image_description="test description 3",
        prompt="test prompt 3",
    )
    db.posts.insert_post(post)
    db.posts.insert_post(post2)
    db.posts.insert_post(post3)
    yield db.select_posts()


@pytest.fixture
def comments(
    characters: List[db.Character], posts: List[db.Post]
) -> Generator[List[db.Comment], None, None]:
    """Creates a number of comments to be used in testing."""
    comment = db.Comment(
        post_id=posts[0]["id"],
        char_id=characters[0]["id"],
        content="test comment",
    )
    comment2 = db.Comment(
        post_id=posts[0]["id"],
        char_id=characters[1]["id"],
        content="test comment 2",
    )
    comment3 = db.Comment(
        post_id=posts[1]["id"],
        char_id=characters[0]["id"],
        content="test comment 3",
    )
    db.comments.insert_comment(comment)
    db.comments.insert_comment(comment2)
    db.comments.insert_comment(comment3)
    yield db.comments.select_comments()
