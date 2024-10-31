"""This file contains the tests for the chatbot/events.py file."""

# pylint: disable=redefined-outer-name unused-argument unused-import too-many-arguments protected-access

import importlib
from typing import List

import database_old as db
from chatbot import Model, generate_event
from not_t.test_chatbot.test_model import model
from not_t.test_database_old.test_characters import char_1
from not_t.test_database_old.test_events import event_1, event_2
from not_t.test_database_old.test_main import db_init
from not_t.test_database_old.test_messages import message_1, message_2
from not_t.test_database_old.test_posts import post_1, post_2
from not_t.test_database_old.test_threads import thread_1
from not_t.test_database_old.test_users import user_1

types_module = importlib.import_module("chatbot.types")
ChatMessage = getattr(types_module, "ChatMessage")
StampedChatMessage = getattr(types_module, "StampedChatMessage")
events_module = importlib.import_module("chatbot.events")
Events = getattr(events_module, "Events")


def test_generate_event(model: Model, char_1: db.Character) -> None:
    """Test the generate_event function."""
    assert char_1["id"]
    generate_event(model, char_1["id"], "event")
    events = db.select_events(db.Event(char_id=char_1["id"]))
    assert len(events) == 1
    assert events[0]["content"] == "Mock event"


def test_turn_message_into_chatmessage(model: Model, message_1: db.Message) -> None:
    """Test the turn_message_into_chatmessage function."""
    chat_message = events_module._turn_message_into_chatmessage(message_1)
    assert chat_message["role"] == message_1["role"]
    assert chat_message["timestamp"] == db.convert_ts_dt(message_1["timestamp"])
    assert chat_message["content"]


def test_turn_event_into_chatmessage(model: Model, event_1: db.Event) -> None:
    """Test the turn_message_into_chatmessage function."""
    chat_message = events_module._turn_event_into_chatmessage(event_1)
    assert chat_message["role"] == "assistant"
    assert chat_message["timestamp"] == db.convert_ts_dt(event_1["timestamp"])
    assert chat_message["content"]


def test_turn_post_into_chatmessage(model: Model, post_1: db.Post) -> None:
    """Test the turn_message_into_chatmessage function."""
    chat_message = events_module._turn_post_into_chatmessage(post_1)
    assert chat_message["role"] == "assistant"
    assert chat_message["timestamp"] == db.convert_ts_dt(post_1["timestamp"])
    assert chat_message["content"]


def test_add_messages_to_log(
    model: Model, char_1: db.Character, message_1: db.Message, message_2: db.Message
) -> None:
    """Test the add_messages_to_log function."""
    chatlog = []
    events_module._add_messages_to_log(char_1["id"], chatlog)
    assert len(chatlog) == 2


def test_add_events_to_log(
    model: Model, char_1: db.Character, event_1: db.Event, event_2: db.Event
) -> None:
    """Test the add_events_to_log function."""
    chatlog = []
    events_module._add_events_to_log(char_1["id"], chatlog)
    assert len(chatlog) == 2


def test_add_posts_to_log(
    model: Model, char_1: db.Character, post_1: db.Post, post_2: db.Post
) -> None:
    """Test the add_posts_to_log function."""
    chatlog = []
    events_module._add_posts_to_log(char_1["id"], chatlog)
    assert len(chatlog) == 2


def test_create_complete_event_log(
    model: Model,
    char_1: db.Character,
    message_1: db.Message,
    message_2: db.Message,
    event_1: db.Event,
    event_2: db.Event,
    post_1: db.Post,
    post_2: db.Post,
) -> None:
    """Test the create_complete_event_log function."""
    chatlog = events_module._create_complete_event_log(char_1["id"])
    assert len(chatlog) == 6
