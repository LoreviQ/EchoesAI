"""This file contains the tests for the chatbot/response.py file."""

# pylint: disable=redefined-outer-name unused-argument unused-import

import importlib

import database as db
from chatbot import Model, new_model
from tests.test_chatbot.test_model import model
from tests.test_database.test_characters import char_1
from tests.test_database.test_main import db_init
from tests.test_database.test_messages import message_1, message_2
from tests.test_database.test_threads import thread_1
from tests.test_database.test_users import user_1

types_module = importlib.import_module("chatbot.types")
ChatMessage = getattr(types_module, "ChatMessage")
response_module = importlib.import_module("chatbot.response")
Messages = getattr(response_module, "Messages")


def test_messages_class(
    model: Model, thread_1: db.Thread, message_1: db.Message, message_2: db.Message
):
    """Test the Messages class."""
    messages = Messages(thread_id=thread_1["id"])
    chatlog = messages.sorted(model=model)
    assert chatlog[0]["role"] == "user"
    assert "test message" in chatlog[0]["content"]
    assert chatlog[1]["role"] == "assistant"
    assert "test response" in chatlog[1]["content"]
    assert len(chatlog) == 2
