"""
This file contains the tests for the chatbot.py file.
"""

# pylint: disable=redefined-outer-name
import os
from typing import Generator

import pytest

from chatbot import Chatbot
from database import DB
from model import new_model


@pytest.fixture
def chatbot() -> Generator[Chatbot, None, None]:
    """
    Create a Chatbot object for testing and teardown after testing.
    """
    test_name = os.environ.get("PYTEST_CURRENT_TEST")
    if test_name is None:
        test_name = "unknown"
    else:
        test_name = test_name.split(":")[-1].split(" ")[0]
    db_path = f"test_database_{test_name}.db"
    db = DB(db_path)
    thread_id = db.post_thread("test_user", "test")
    db.post_message(thread_id, "How can I help?", "assistant")
    db.post_message(thread_id, "This is my test message", "user")
    model = new_model(mocked=True)
    chatbot = Chatbot(thread_id=thread_id, database=db, model=model)
    yield chatbot
    os.remove(db_path)


def test_initialization(chatbot: Chatbot) -> None:
    """
    Test the initialization of the Chatbot class.
    """
    assert chatbot.thread == 1
    assert chatbot.username == "test_user"
    assert chatbot.phase == 0
    assert chatbot.character_info["char"] == "Test Character"
    assert chatbot.character_info["description"] == "A test character"
    assert chatbot.character_info["age"] == "25"
    assert chatbot.character_info["phases"][0]["name"] == "Phase 1"
    assert chatbot.chatlog[0]["role"] == "assistant"
    assert chatbot.chatlog[0]["content"] == "How can I help?"
    assert chatbot.chatlog[1]["role"] == "user"
    assert chatbot.chatlog[1]["content"] == "This is my test message"


def test_get_system_message(chatbot: Chatbot) -> None:
    """
    Test the set_system_message method of the Chatbot class.
    """
    system_message = chatbot.get_system_message("chat_message")
    assert system_message[0]["role"] == "system"
    assert "You are an expert actor who" in system_message[0]["content"]
    system_message = chatbot.get_system_message("time_checker")
    assert system_message[0]["role"] == "system"
    assert "response frequency of Test Character" in system_message[0]["content"]
    assert "Response for phase 1" in system_message[0]["content"]


def test_get_response(chatbot: Chatbot) -> None:
    """
    Test the get_response method of the Chatbot class.
    """
    system_message = chatbot.get_system_message("chat_message")
    response = chatbot.get_response(system_message, chatbot.chatlog)
    assert response["role"] == "assistant"
    assert "Mock response" in response["content"]
