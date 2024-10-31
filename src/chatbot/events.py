"""
Handles the functions required to generate an event from the chatbot.
I.E. Events only containing the character
"""

import json
from datetime import datetime, timezone
from typing import List, cast

import database_old as db

from .main import _generate_text, _get_system_message
from .model import Model
from .types import MAX_TOKENS, ChatMessage, StampedChatMessage


def _create_complete_event_log(
    char_id: int,
    events: bool = True,
    messages: bool = True,
    posts: bool = True,
    model: Model | None = None,
) -> List[ChatMessage]:
    """
    Create an event log for a character.
    """
    if not any([events, messages, posts]):
        raise ValueError("At least one of events, messages, or posts must be True.")
    chatlog: List[StampedChatMessage] = []
    if messages:
        _add_messages_to_log(char_id, chatlog)
    if events:
        _add_events_to_log(char_id, chatlog)
    if posts:
        _add_posts_to_log(char_id, chatlog)
    chatlog = sorted(chatlog, key=lambda x: x["timestamp"])
    chatlog = [cast(ChatMessage, x) for x in chatlog]
    if not model:
        # if no model is provided, don't truncate and return early
        return chatlog
    truncated_log = chatlog[:]
    while model.token_count(truncated_log) > MAX_TOKENS:
        truncated_log.pop(0)
    return truncated_log


def _add_messages_to_log(char_id: int, chat_log: List[StampedChatMessage]) -> None:
    messages = db.select_messages_by_character(char_id)
    for message in messages:
        if not all(
            [
                message["timestamp"],
                message["content"],
                message["role"],
                message["thread_id"],
            ]
        ):
            continue
        chat_log.append(_turn_message_into_chatmessage(message))


def _turn_message_into_chatmessage(message: db.Message) -> StampedChatMessage:
    thread = db.select_thread(message["thread_id"])
    char = db.select_character_by_id(thread["char_id"])
    user = db.select_user_by_id(thread["user_id"])
    timestamp_str: str = message["timestamp"]
    timestamp_dt = db.convert_ts_dt(timestamp_str)
    content = {
        "type": "message",
        "time_message_was_sent": timestamp_str,
        "message": message["content"],
    }
    if message["role"] == "user":
        content["sent_by"] = user["username"]
        content["sent_to"] = char["name"]
    else:
        content["sent_by"] = char["name"]
        content["sent_to"] = user["username"]
    chatmessage = StampedChatMessage(
        role=message["role"],
        content=json.dumps(content),
        timestamp=db.convert_ts_dt(timestamp_dt),
    )
    return chatmessage


def _add_events_to_log(char_id: int, chat_log: List[StampedChatMessage]) -> None:
    events = db.events.select_events(db.Event(char_id=char_id))
    for event in events:
        chat_log.append(_turn_event_into_chatmessage(event))


def _turn_event_into_chatmessage(event: db.Event) -> StampedChatMessage:
    timestamp_str: str = event["timestamp"]
    timestamp_dt = db.convert_ts_dt(timestamp_str)
    content = {
        "type": event["type"],
        "time_event_occurred": timestamp_str,
        "event": event["content"],
    }
    chatmessage = StampedChatMessage(
        role="assistant",
        content=json.dumps(content),
        timestamp=timestamp_dt,
    )
    return chatmessage


def _add_posts_to_log(char_id: int, chat_log: List[StampedChatMessage]) -> None:
    posts = db.posts.select_posts(db.Post(char_id=char_id))
    for post in posts:
        chat_log.append(_turn_post_into_chatmessage(post))


def _turn_post_into_chatmessage(post: db.Post) -> StampedChatMessage:
    timestamp_str: str = post["timestamp"]
    timestamp_dt = db.convert_ts_dt(timestamp_str)
    if post["image_post"]:
        content = {
            "type": "image_post",
            "time_post_was_made": timestamp_str,
            "image_description": post["description"],
            "caption": post["caption"],
        }
    else:
        content = {
            "type": "text_post",
            "time_post_was_made": timestamp_str,
            "post": post["description"],
        }
    if post["image_post"]:
        content["caption"] = post["caption"]
    chatmessage = StampedChatMessage(
        role="assistant",
        content=json.dumps(content),
        timestamp=timestamp_dt,
    )
    return chatmessage


def generate_event(model: Model, character_id: int, event_type: str) -> None:
    """
    Generate an event message.
    """
    character = db.select_character_by_id(character_id)
    sys_message = _get_system_message("event", character)
    chatlog = _create_complete_event_log(character_id, model=model)
    timestamp = db.convert_dt_ts(datetime.now(timezone.utc))
    match event_type:
        case "thought":
            content = f"The time is currently {timestamp}. Generate a thought"
        case "event":
            content = f"The time is currently {timestamp}. Generate an event"

    chatlog.append(ChatMessage(role="user", content=content))
    response = _generate_text(model, sys_message, chatlog)
    event = db.Event(
        char_id=character["id"],
        type=event_type,
        content=response["content"],
    )
    db.events.insert_event(event)
