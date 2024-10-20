"""
This file contains the tests for the chatbot.py file.
"""

# pylint: disable=redefined-outer-name, protected-access
import os
from datetime import datetime, timedelta, timezone
from typing import Generator

import pytest

from chatbot import Chatbot, _parse_time
from database import DB
from model import Model, ModelMocked


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
    model = Model(ModelMocked("short"))
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


def test_get_system_message(chatbot: Chatbot) -> None:
    """
    Test the set_system_message method of the Chatbot class.
    """
    system_message = chatbot.get_system_message("chat")
    assert system_message[0]["role"] == "system"
    assert "You are an expert actor who" in system_message[0]["content"]
    system_message = chatbot.get_system_message("time")
    assert system_message[0]["role"] == "system"
    assert "response frequency of Test Character" in system_message[0]["content"]
    assert "Response for phase 1" in system_message[0]["content"]


def test_generate_text(chatbot: Chatbot) -> None:
    """
    Test the get_response method of the Chatbot class.
    """
    system_message = chatbot.get_system_message("chat")
    messages = chatbot.database.get_messages_by_thread(chatbot.thread)
    chatlog = chatbot._convert_messages_to_chatlog(messages)
    response = chatbot._generate_text(system_message, chatlog)

    assert response["role"] == "assistant"
    assert "Mock response" in response["content"]


def test_response_cycle_short(chatbot: Chatbot) -> None:
    """
    Test the response cycle of the Chatbot class when responses are short.
    """
    chatbot.response_cycle()
    messages = chatbot.database.get_messages_by_thread(chatbot.thread)
    assert messages[-1]["role"] == "assistant"
    assert "Mock response" in messages[-1]["content"]


def test_response_cycle_long(chatbot: Chatbot) -> None:
    """
    Test the response cycle of the Chatbot class when responses are long.
    """
    chatbot.model = Model(ModelMocked("long"))
    chatbot.response_cycle()
    messages = chatbot.database.get_messages_by_thread(chatbot.thread)
    assert messages[-1]["role"] == "assistant"
    assert "Mock response" in messages[-1]["content"]
    assert messages[-1]["timestamp"] > datetime.now(timezone.utc)


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
