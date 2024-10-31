"""This file contains the tests for the chatbot/main.py file."""

# pylint: disable=redefined-outer-name unused-argument unused-import

import importlib
from datetime import timedelta

import pytest

import database as db
from chatbot import Model
from tests.test_chatbot.test_model import model
from tests.test_database.test_characters import char_1
from tests.test_database.test_main import test_db
from tests.test_database.test_threads import thread_1
from tests.test_database.test_users import user_1

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


def test_get_system_message_chat(model: Model, thread_1: db.Thread) -> None:
    """
    Test the _get_system_message function.
    """
    system_message = _get_system_message("chat", thread_1)
    assert system_message["role"] == "system"
    assert "You are an expert actor who" in system_message["content"]
    system_message = _get_system_message("time", thread_1)
    assert system_message["role"] == "system"
    assert "current response frequency of" in system_message["content"]


def test_get_system_message_time(model: Model, thread_1: db.Thread) -> None:
    """
    Test the _get_system_message function.
    """
    system_message = _get_system_message("chat", thread_1)
    assert system_message["role"] == "system"
    assert "You are an expert actor who" in system_message["content"]


def test_get_system_message_invalid_thread(model: Model) -> None:
    """
    Test the _get_system_message function.
    """
    fake_thread = db.Thread(
        id=0,
        user_id=0,
        char_id=0,
        started="2021-01-01 00:00:00",
        phase=0,
    )
    with pytest.raises(AssertionError):
        _get_system_message("chat", fake_thread)


def test_get_system_message_invalid_character(model: Model) -> None:
    """
    Test the _get_system_message function.
    """
    fake_thread = db.Thread(
        id=0,
        user_id=0,
        char_id=5,
        started="2021-01-01 00:00:00",
        phase=0,
    )
    with pytest.raises(ValueError):
        _get_system_message("chat", fake_thread)


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
