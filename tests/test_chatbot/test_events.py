"""This file contains the tests for the chatbot/events.py file."""

# pylint: disable=redefined-outer-name unused-argument unused-import too-many-arguments protected-access

import importlib
from io import BytesIO
from typing import Generator
from unittest.mock import MagicMock

import pytest
from google.cloud import storage

import database as db
from chatbot import Model, generate_event, generate_social_media_post
from tests.test_chatbot.test_model import model
from tests.test_database.test_characters import char_1
from tests.test_database.test_events import event_1, event_2
from tests.test_database.test_main import db_init
from tests.test_database.test_messages import message_1, message_2
from tests.test_database.test_posts import post_1, post_2
from tests.test_database.test_threads import thread_1
from tests.test_database.test_users import user_1

types_module = importlib.import_module("chatbot.types")
ChatMessage = getattr(types_module, "ChatMessage")
events_module = importlib.import_module("chatbot.events")
Events = getattr(events_module, "Events")
_civitai_generate_image = getattr(events_module, "_civitai_generate_image")
_generate_image_post = getattr(events_module, "_generate_image_post")
_generate_text_post = getattr(events_module, "_generate_text_post")
_upload_image_to_gcs = getattr(events_module, "_upload_image_to_gcs")


@pytest.fixture
def image_stream() -> Generator[BytesIO, None, None]:
    """Return a BytesIO image stream."""
    with open("tests/test_chatbot/test_image.jpg", "rb") as image_file:
        image_stream = BytesIO(image_file.read())
        image_stream.seek(0)  # Reset stream position
        yield image_stream


def test_events_class_sorted(
    model: Model,
    char_1: db.Character,
    thread_1: db.Thread,
    message_1: db.Message,
    message_2: db.Message,
    post_1: db.Post,
    post_2: db.Post,
    event_1: db.Event,
    event_2: db.Event,
) -> None:
    """Test the Events class sorted method"""
    events = Events(char_1["id"], True, True, True)
    chatlog = events.sorted(model=model)
    assert len(chatlog) == 6


def test_events_class_convert_messages_to_chatlog(
    model: Model,
    char_1: db.Character,
    thread_1: db.Thread,
    message_1: db.Message,
    message_2: db.Message,
) -> None:
    """Test the Events class convert_messages_to_chatlog method"""
    events = Events(char_1["id"], False, True, False)
    chatlog = events._convert_messages_to_chatlog()
    assert len(chatlog) == 2


def test_events_class_convert_events_to_chatlog(
    model: Model,
    char_1: db.Character,
    event_1: db.Event,
    event_2: db.Event,
) -> None:
    """Test the Events class convert_events_to_chatlog method"""
    events = Events(char_1["id"], True, False, False)
    chatlog = events._convert_events_to_chatlog()
    assert len(chatlog) == 2


def test_events_class_convert_posts_to_chatlog(
    model: Model,
    char_1: db.Character,
    post_1: db.Post,
    post_2: db.Post,
) -> None:
    """Test the Events class convert_posts_to_chatlog method"""
    events = Events(char_1["id"], False, False, True)
    chatlog = events._convert_posts_to_chatlog()
    assert len(chatlog) == 2


def test_generate_event(model: Model, char_1: db.Character) -> None:
    """Test the generate_event function."""
    assert char_1["id"]
    generate_event(model, char_1["id"], "event")
    events = db.select_events(db.Event(char_id=char_1["id"]))
    assert len(events) == 1
    assert events[0]["content"] == "Mock event"


@pytest.mark.slow
def test_civitai_generate_image(
    monkeypatch: pytest.MonkeyPatch, model: Model, char_1: db.Character, post_1: db.Post
) -> None:
    """Test the _civitai_generate_image function."""
    monkeypatch.setenv(
        "GOOGLE_APPLICATION_CREDENTIALS",
        "/home/lorevi/workspace/keys/echoes-ai-deploy.json",
    )
    prompt = "cute, mascot, robot, drinking coffee, funny, test robot,"
    _civitai_generate_image(char_1, post_1["id"], prompt)
    posts = db.select_posts(db.Post(id=post_1["id"]))
    assert posts[0]["image_path"] == f"{char_1['name']}/posts/{post_1['id']}.jpg"


def test_generate_image_post(
    monkeypatch: pytest.MonkeyPatch, model: Model, char_1: db.Character
) -> None:
    """Test the _generate_image_post function."""
    mock_civitai_generate_image = MagicMock()
    monkeypatch.setattr(
        "chatbot.events._civitai_generate_image", mock_civitai_generate_image
    )
    _generate_image_post(model, char_1)

    # assert _civitai_generate_image was called with the expected arguments
    mock_civitai_generate_image.assert_called_once_with(char_1, 1, "Mock SD prompt")

    posts = db.select_posts(db.Post(char_id=char_1["id"]))
    assert len(posts) == 1
    assert posts[0]["description"] == "Mock Image Description"
    assert posts[0]["prompt"] == "Mock SD prompt"
    assert posts[0]["caption"] == "Mock Caption"
    assert posts[0]["image_post"]


def test_generate_text_post(model: Model, char_1: db.Character) -> None:
    """Test the _generate_text_post function."""
    _generate_text_post(model, char_1)

    posts = db.select_posts(db.Post(char_id=char_1["id"]))
    assert len(posts) == 1
    assert posts[0]["description"] == "Mock response"
    assert posts[0]["prompt"] == ""
    assert posts[0]["caption"] == ""
    assert not posts[0]["image_post"]


def test_generate_social_media_post_text(
    monkeypatch: pytest.MonkeyPatch, model: Model, char_1: db.Character
) -> None:
    """Test the generate_social_media_post function for text post generation."""
    assert char_1["id"]
    assert char_1["path_name"]
    character_full = db.select_character(char_1["path_name"])
    mock_generate_text_post = MagicMock()
    mock_generate_image_post = MagicMock()
    monkeypatch.setattr("chatbot.events._generate_text_post", mock_generate_text_post)
    monkeypatch.setattr("chatbot.events._generate_image_post", mock_generate_image_post)
    monkeypatch.setattr("random.random", lambda: 0.5)  # Force text post generation

    generate_social_media_post(model, char_1["id"])

    mock_generate_text_post.assert_called_once_with(model, character_full)
    mock_generate_image_post.assert_not_called()


def test_generate_social_media_post_image(
    monkeypatch: pytest.MonkeyPatch, model: Model, char_1: db.Character
) -> None:
    """Test the generate_social_media_post function for image post generation."""
    assert char_1["id"]
    assert char_1["path_name"]
    character_full = db.select_character(char_1["path_name"])
    mock_generate_text_post = MagicMock()
    mock_generate_image_post = MagicMock()
    monkeypatch.setattr("chatbot.events._generate_text_post", mock_generate_text_post)
    monkeypatch.setattr("chatbot.events._generate_image_post", mock_generate_image_post)
    monkeypatch.setattr("random.random", lambda: 0.8)  # Force image post generation

    generate_social_media_post(model, char_1["id"])

    mock_generate_text_post.assert_not_called()
    mock_generate_image_post.assert_called_once_with(model, character_full)


def test_upload_image_to_gcs(
    monkeypatch: pytest.MonkeyPatch, image_stream: BytesIO
) -> None:
    """Test the _upload_image_to_gcs function."""
    monkeypatch.setenv(
        "GOOGLE_APPLICATION_CREDENTIALS",
        "/home/lorevi/workspace/keys/echoes-ai-deploy.json",
    )
    destination_blob_name = "test-folder/test-image.jpg"
    _upload_image_to_gcs(image_stream, destination_blob_name)

    # Verify the image was uploaded
    storage_client = storage.Client()
    bucket = storage_client.bucket("echoesai-public-images")
    blob = bucket.blob(destination_blob_name)
    assert blob.exists()

    # Clean up the uploaded test image
    blob.delete()
