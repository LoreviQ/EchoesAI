"""This file contains the tests for the chatbot/events.py file."""

# pylint: disable=redefined-outer-name unused-argument unused-import too-many-arguments protected-access

import importlib
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import database as db
from chatbot import Model, generate_event

from .fixtures import model

events_module = importlib.import_module("chatbot.events")


@patch("database.select_thread")
@patch("database.select_character_by_id")
@patch("database.select_user_by_id")
def test_turn_message_into_chatmessage(
    mock_select_user_by_id: MagicMock,
    mock_select_character_by_id: MagicMock,
    mock_select_thread: MagicMock,
    model: Model,
) -> None:
    """Test the turn_message_into_chatmessage function."""
    user = db.User(id=1, username="test", email="test@test.com")
    character = db.Character(id=1, name="test", path_name="test_path")
    thread = db.Thread(id=1, char_id=character["id"], user_id=user["id"])
    message = db.Message(
        id=1,
        thread_id=thread["id"],
        role="user",
        content="Hi!",
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=20),
    )
    mock_select_thread.return_value = thread
    mock_select_character_by_id.return_value = character
    mock_select_user_by_id.return_value = user
    chat_message = events_module._turn_message_into_chatmessage(message)
    assert chat_message["role"] == message["role"]
    assert chat_message["timestamp"] == message["timestamp"]
    assert chat_message["content"]
    assert mock_select_thread.called_oce_with(message["thread_id"])
    assert mock_select_character_by_id.called_once_with(thread["char_id"])
    assert mock_select_user_by_id.called_once_with(thread["user_id"])


def test_turn_event_into_chatmessage(model: Model) -> None:
    """Test the turn_message_into_chatmessage function."""
    event = db.Event(
        id=1,
        char_id=1,
        type="event",
        content="Mock event",
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=20),
    )
    chat_message = events_module._turn_event_into_chatmessage(event)
    assert chat_message["role"] == "assistant"
    assert chat_message["timestamp"] == event["timestamp"]
    assert chat_message["content"]


def test_turn_post_into_chatmessage(model: Model) -> None:
    """Test the turn_message_into_chatmessage function."""
    post = db.Post(
        id=1,
        char_id=1,
        content="Mock post",
        image_post=False,
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=20),
    )
    chat_message = events_module._turn_post_into_chatmessage(post)
    assert chat_message["role"] == "assistant"
    assert chat_message["timestamp"] == post["timestamp"]
    assert chat_message["content"]
