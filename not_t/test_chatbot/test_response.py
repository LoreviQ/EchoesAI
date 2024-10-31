"""This file contains the tests for the chatbot/response.py file."""

# pylint: disable=redefined-outer-name unused-argument unused-import

import importlib
from datetime import datetime, timedelta, timezone

import database_old as db
from chatbot import Model, new_model, response_cycle
from not_t.test_chatbot.test_model import model
from not_t.test_database_old.test_characters import char_1
from not_t.test_database_old.test_main import db_init
from not_t.test_database_old.test_messages import message_1, message_2
from not_t.test_database_old.test_threads import thread_1
from not_t.test_database_old.test_users import user_1

types_module = importlib.import_module("chatbot.types")
ChatMessage = getattr(types_module, "ChatMessage")
response_module = importlib.import_module("chatbot.response")
Messages = getattr(response_module, "Messages")
_get_response_time = getattr(response_module, "_get_response_time")
_get_response_and_submit = getattr(response_module, "_get_response_and_submit")


def test_messages_class(
    model: Model, thread_1: db.Thread, message_1: db.Message, message_2: db.Message
) -> None:
    """Test the Messages class."""
    messages = Messages(thread_id=thread_1["id"])
    chatlog = messages.sorted(model=model)
    assert chatlog[0]["role"] == "user"
    assert "test message" in chatlog[0]["content"]
    assert chatlog[1]["role"] == "assistant"
    assert "test response" in chatlog[1]["content"]
    assert len(chatlog) == 2


def test_get_response_time(model: Model, thread_1: db.Thread) -> None:
    """Test the _get_response_time function."""
    response_time = _get_response_time(model, thread_1)
    assert response_time == timedelta(seconds=1)


def test_get_response_and_submit(model: Model, thread_1: db.Thread) -> None:
    """Test the _get_response_and_submit function."""
    _get_response_and_submit(model, thread_1, datetime.now(timezone.utc))
    assert thread_1["id"]
    messages = db.select_messages_by_thread(thread_1["id"])
    assert len(messages) == 1


def test_response_cycle(model: Model, thread_1: db.Thread) -> None:
    """Test the response_cycle function."""
    assert thread_1["id"]
    response_cycle(model, thread_1["id"])
    messages = db.select_messages_by_thread(thread_1["id"])
    assert len(messages) == 1
