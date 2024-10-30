"""This file contains the tests for the chatbot/events.py file."""

# pylint: disable=redefined-outer-name unused-argument unused-import too-many-arguments protected-access

import importlib

import database as db
from chatbot import Model, generate_event
from tests.test_chatbot.test_model import model
from tests.test_database.test_characters import char_1
from tests.test_database.test_events import event_1, event_2
from tests.test_database.test_main import db_init
from tests.test_database.test_messages import message_1, message_2
from tests.test_database.test_posts import post_1, post_2
from tests.test_database.test_threads import thread_1
from tests.test_database.test_users import user_1

types_module = importlib.import_module("chatbot.types")
ChatMessage = getattr(types_module, "ChatMessage")
events_module = importlib.import_module("chatbot.events")
Events = getattr(events_module, "Events")


def test_events_class_sorted(
    model: Model,
    char_1: db.Character,
    thread_1: db.Thread,
    message_1: db.Message,
    message_2: db.Message,
    post_1: db.Post,
    post_2: db.Post,
    event_1: db.Event,
    event_2: db.Event,
) -> None:
    """Test the Events class sorted method"""
    events = Events(char_1["id"], True, True, True)
    chatlog = events.sorted(model=model)
    assert len(chatlog) == 6


def test_events_class_convert_messages_to_chatlog(
    model: Model,
    char_1: db.Character,
    thread_1: db.Thread,
    message_1: db.Message,
    message_2: db.Message,
) -> None:
    """Test the Events class convert_messages_to_chatlog method"""
    events = Events(char_1["id"], False, True, False)
    chatlog = events._convert_messages_to_chatlog()
    assert len(chatlog) == 2


def test_events_class_convert_events_to_chatlog(
    model: Model,
    char_1: db.Character,
    event_1: db.Event,
    event_2: db.Event,
) -> None:
    """Test the Events class convert_events_to_chatlog method"""
    events = Events(char_1["id"], True, False, False)
    chatlog = events._convert_events_to_chatlog()
    assert len(chatlog) == 2


def test_events_class_convert_posts_to_chatlog(
    model: Model,
    char_1: db.Character,
    post_1: db.Post,
    post_2: db.Post,
) -> None:
    """Test the Events class convert_posts_to_chatlog method"""
    events = Events(char_1["id"], False, False, True)
    chatlog = events._convert_posts_to_chatlog()
    assert len(chatlog) == 2


def test_generate_event(model: Model, char_1: db.Character) -> None:
    """Test the generate_event function."""
    assert char_1["id"]
    generate_event(model, char_1["id"], "event")
    events = db.select_events(db.Event(char_id=char_1["id"]))
    assert len(events) == 1
    assert events[0]["content"] == "Mock event"
