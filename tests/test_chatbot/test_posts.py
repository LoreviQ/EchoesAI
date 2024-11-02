"""This file contains the tests for the chatbot/events.py file."""

# pylint: disable=redefined-outer-name unused-argument unused-import too-many-arguments protected-access

import importlib
from io import BytesIO
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from google.cloud import storage

import database as db
from chatbot import Model, generate_social_media_post

from .fixtures import image_stream, model

types_module = importlib.import_module("chatbot.types")
ChatMessage = getattr(types_module, "ChatMessage")
posts_module = importlib.import_module("chatbot.posts")
_civitai_generate_image = getattr(posts_module, "_civitai_generate_image")
_upload_image_to_gcs = getattr(posts_module, "_upload_image_to_gcs")


@pytest.mark.slow
@patch("database.update_post_with_image_path")
def test_civitai_generate_image(
    mock_update_post_with_image_path: MagicMock, model: Model
) -> None:
    """Test the _civitai_generate_image function."""
    char = db.Character(id=1, name="test", path_name="test_path")
    post = db.Post(id=1, char_id=char["id"])
    prompt = "cute, mascot, robot, drinking coffee, funny, test robot,"
    _civitai_generate_image(char, post["id"], prompt)
    posts = db.select_posts(db.Post(id=post["id"]))
    assert posts[0]["image_path"] == f"{char['name']}/posts/{post['id']}.jpg"


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
