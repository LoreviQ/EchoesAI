"""This file contains the tests for the chatbot/main.py file."""

# pylint: disable=redefined-outer-name unused-argument unused-import

import importlib
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest

import database as db
from chatbot import Model

from .fixtures import model

main_module = importlib.import_module("chatbot.main")
_get_system_message = getattr(main_module, "_get_system_message")
_parse_time = getattr(main_module, "_parse_time")
_generate_text = getattr(main_module, "_generate_text")

types_module = importlib.import_module("chatbot.types")
ChatMessage = getattr(types_module, "ChatMessage")


def test_generate_text(model: Model) -> None:
    """
    Test the _generate_text function.
    """
    system_message = ChatMessage(role="system", content="You are an assistant.")
    chat = [
        ChatMessage(role="user", content="Hi!"),
    ]
    response = _generate_text(model, system_message, chat)
    assert response["role"] == "assistant"
    assert response["content"] == "Mock response"


def test_generate_text_no_input(model: Model) -> None:
    """
    Test the _generate_text function with no input.
    """
    system_message = ChatMessage(role="system", content="You are an assistant.")
    response = _generate_text(model, system_message, [])
    assert response["role"] == "assistant"
    assert response["content"] == "Mock response"


@patch("database.select_character_by_id")
@patch("database.select_user_by_id")
def test_get_system_message_chat(
    mock_select_user_by_id: MagicMock,
    mock_select_character_by_id: MagicMock,
    model: Model,
) -> None:
    """
    Test the _get_system_message function.
    """
    user = db.User(id=1, username="test", email="test@test.com")
    mock_select_user_by_id.return_value = user
    character = db.Character(id=1, name="test")
    mock_select_character_by_id.return_value = character
    thread = db.Thread(
        id=1,
        user_id=user["id"],
        char_id=character["id"],
    )
    system_message = _get_system_message("chat", thread)
    assert system_message["role"] == "system"
    assert "You are an expert actor who" in system_message["content"]
    system_message = _get_system_message("time", thread)
    assert system_message["role"] == "system"
    assert "current response frequency of" in system_message["content"]
    assert mock_select_user_by_id.called_once_with(thread["user_id"])
    assert mock_select_character_by_id.called_once_with(thread["char_id"])


@patch("database.select_character_by_id")
@patch("database.select_user_by_id")
def test_get_system_message_time(
    mock_select_user_by_id: MagicMock,
    mock_select_character_by_id: MagicMock,
    model: Model,
) -> None:
    """
    Test the _get_system_message function.
    """
    user = db.User(id=1, username="test", email="test@test.com")
    mock_select_user_by_id.return_value = user
    character = db.Character(id=1, name="test")
    mock_select_character_by_id.return_value = character
    thread = db.Thread(
        id=1,
        user_id=user["id"],
        char_id=character["id"],
    )
    system_message = _get_system_message("chat", thread)
    assert system_message["role"] == "system"
    assert "You are an expert actor who" in system_message["content"]
    assert mock_select_user_by_id.called_once_with(thread["user_id"])
    assert mock_select_character_by_id.called_once_with(thread["char_id"])


def test_parse_time() -> None:
    """
    Test the _parse_time function.
    """
    # Basic tests
    time = "1d 2h 3m 4s"
    assert _parse_time(time) == timedelta(days=1, hours=2, minutes=3, seconds=4)
    time = "2h 3m 4s"
    assert _parse_time(time) == timedelta(hours=2, minutes=3, seconds=4)
    time = "3m 4s"
    assert _parse_time(time) == timedelta(minutes=3, seconds=4)
    time = "1d 2h 3m"
    assert _parse_time(time) == timedelta(days=1, hours=2, minutes=3)
    time = "2h 3m"
    assert _parse_time(time) == timedelta(hours=2, minutes=3)
    time = "3m"
    assert _parse_time(time) == timedelta(minutes=3)
    time = "4s"
    assert _parse_time(time) == timedelta(seconds=4)

    # Messy tests
    time = "Sure. The time is: 2h30s"
    assert _parse_time(time) == timedelta(hours=2, seconds=30)
    time = "I would wait 5m and 16s"
    assert _parse_time(time) == timedelta(minutes=5, seconds=16)
    time = "1d3h and I think 22m"
    assert _parse_time(time) == timedelta(days=1, hours=3, minutes=22)
    time = "I would wait 55s no wait, 14s"  # Always take first
    assert _parse_time(time) == timedelta(seconds=55)
    time = "3m and 50s. What do you think?"
    assert _parse_time(time) == timedelta(minutes=3, seconds=50)
    time = "I can't wait!"
    assert _parse_time(time) == timedelta(seconds=0)
