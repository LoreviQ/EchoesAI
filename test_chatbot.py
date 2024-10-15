import re

from chatbot import Chatbot


def test_initialization():
    chatbot = Chatbot(username="test_user", character="test")
    assert chatbot.username == "test_user"
    assert chatbot.character_info["char"] == "Test Character"
    assert chatbot.character_info["description"] == "A test character"
    assert chatbot.character_info["age"] == "25"
    assert chatbot.character_info["phases"][0]["name"] == "Phase 1"
    assert chatbot.chat[0]["role"] == "system"
    assert "You are an expert actor who can" in chatbot.chat[0]["content"]
    assert "Loves: Coding" in chatbot.chat[0]["content"]
    assert "The story follows the scenario: Test scenario" in chatbot.chat[0]["content"]
    assert chatbot.chat[1]["role"] == "assistant"
    assert chatbot.chat[1]["content"] == "Hello, I am your assistant."


def test_set_system_message():
    chatbot = Chatbot(username="test_user", character="test")
    chatbot.set_system_message(chatbot.chat, "time_checker")
    assert chatbot.chat[0]["role"] == "system"
    assert "response frequency of Test Character" in chatbot.chat[0]["content"]
    assert "Response for phase 1" in chatbot.chat[0]["content"]


def test_add_message():
    chatbot = Chatbot(username="test_user", character="test")
    chatbot.add_message({"role": "user", "content": "Test message"})
    assert chatbot.chat[-1]["role"] == "user"
    assert chatbot.chat[-1]["content"] == "Test message"


def test_get_response():
    chatbot = Chatbot(username="test_user", character="test")
    chatbot.add_message({"role": "user", "content": "Test message"})
    response = chatbot.get_response()
    assert response["role"] == "assistant"


def test_check_time():
    chatbot = Chatbot(username="test_user", character="test")
    chatbot.add_message({"role": "user", "content": "Test message"})
    time = chatbot.check_time(new_check_chain=True)
    pattern = r"(?:(\d+)d\s*)?(?:(\d+)h\s*)?(?:(\d+)m\s*)?(?:(\d+)s\s*)?"
    assert re.match(pattern, time)
    time = chatbot.check_time(new_message={"role": "user", "content": "Test message"})
    assert re.match(pattern, time)
