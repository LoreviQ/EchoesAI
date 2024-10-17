"""
This file contains the tests for the chatbot.py file.
"""

# pylint: disable=redefined-outer-name
import os
from typing import Generator

import pytest

from chatbot import Chatbot
from database import DB


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
    db = DB(f"test_database_{test_name}.db")
    chatbot = Chatbot(username="test_user", character="test", thread_id=1, database=db)
    chatbot.new_model(mocked=True)
    yield chatbot
    db.conn.close()
    os.remove(f"test_database_{test_name}.db")


def test_initialization(chatbot: Chatbot) -> None:
    """
    Test the initialization of the Chatbot class.
    """
    assert chatbot.username == "test_user"
    assert chatbot.character_info["char"] == "Test Character"
    assert chatbot.character_info["description"] == "A test character"
    assert chatbot.character_info["age"] == "25"
    assert chatbot.character_info["phases"][0]["name"] == "Phase 1"
    assert chatbot.primary_system_message["role"] == "system"
    assert (
        "You are an expert actor who can" in chatbot.primary_system_message["content"]
    )
    assert "Loves: Coding" in chatbot.primary_system_message["content"]
    assert (
        "The story follows the scenario: Test scenario"
        in chatbot.primary_system_message["content"]
    )
    assert chatbot.primary_chat[0]["role"] == "assistant"
    assert chatbot.primary_chat[0]["content"] == "Hello, I am your assistant."


def test_get_system_message(chatbot: Chatbot) -> None:
    """
    Test the set_system_message method of the Chatbot class.
    """
    system_message = chatbot.get_system_message("time_checker")
    assert system_message["role"] == "system"
    assert "response frequency of Test Character" in system_message["content"]
    assert "Response for phase 1" in system_message["content"]


def test_add_message(chatbot: Chatbot) -> None:
    """
    Test the add_message method of the Chatbot class.
    """
    chatbot.add_message({"role": "user", "content": "Test message"})
    assert chatbot.primary_chat[-1]["role"] == "user"
    assert chatbot.primary_chat[-1]["content"] == "Test message"


def test_get_response(chatbot: Chatbot) -> None:
    """
    Test the get_response method of the Chatbot class.
    """
    chatbot.add_message({"role": "user", "content": "Test message"})
    response = chatbot.get_response()
    assert response["role"] == "assistant"
    assert "Mock response" in response["content"]
