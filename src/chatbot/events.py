"""
Handles the functions required to generate an event from the chatbot.
I.E. Events only containing the character
"""

import json
from datetime import datetime, timezone
from typing import List, cast

import database as db

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
    sorted_chatlog = [cast(ChatMessage, x) for x in chatlog]
    if not model:
        # if no model is provided, don't truncate and return early
        return sorted_chatlog
    truncated_log = sorted_chatlog[:]
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
    content = {
        "type": "message",
        "time_message_was_sent": message["timestamp"].isoformat(),
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
        timestamp=message["timestamp"],
    )
    return chatmessage


def _add_events_to_log(char_id: int, chat_log: List[StampedChatMessage]) -> None:
    events = db.events.select_events(db.Event(char_id=char_id))
    for event in events:
        chat_log.append(_turn_event_into_chatmessage(event))


def _turn_event_into_chatmessage(event: db.Event) -> StampedChatMessage:
    content = {
        "type": event["type"],
        "time_event_occurred": event["timestamp"].isoformat(),
        "event": event["content"],
    }
    chatmessage = StampedChatMessage(
        role="assistant",
        content=json.dumps(content),
        timestamp=event["timestamp"],
    )
    return chatmessage


def _add_posts_to_log(char_id: int, chat_log: List[StampedChatMessage]) -> None:
    posts = db.posts.select_posts(db.Post(char_id=char_id))
    for post in posts:
        chat_log.append(_turn_post_into_chatmessage(post))


def _turn_post_into_chatmessage(post: db.Post) -> StampedChatMessage:
    if post["image_post"]:
        content = {
            "type": "image_post",
            "time_post_was_made": post["timestamp"].isoformat(),
            "image_description": post["image_description"],
            "caption": post["content"],
        }
    else:
        content = {
            "type": "text_post",
            "time_post_was_made": post["timestamp"].isoformat(),
            "post": post["content"],
        }
    chatmessage = StampedChatMessage(
        role="assistant",
        content=json.dumps(content),
        timestamp=post["timestamp"],
    )
    return chatmessage


def generate_event(model: Model, character_id: int, event_type: str) -> None:
    """
    Generate an event message.
    """
    character = db.select_character_by_id(character_id)
    sys_message = _get_system_message("event", character)
    chatlog = _create_complete_event_log(character_id, model=model)
    now = datetime.now(timezone.utc).isoformat()
    match event_type:
        case "thought":
            content = f"The time is currently {now}. Generate a thought"
        case "event":
            content = f"The time is currently {now}. Generate an event"

    chatlog.append(ChatMessage(role="user", content=content))
    response = _generate_text(model, sys_message, chatlog)
    content = _parse_response_event(response["content"], event_type)
    event = db.Event(
        char_id=character["id"],
        type=event_type,
        content=response["content"],
    )
    db.events.insert_event(event)


def _parse_response_event(response_json: str, event_type: str) -> str:
    """
    Parses the JSON string from the model response and returns the 'event' component.
    Checking the type is the called type.
    """
    try:
        response_data = json.loads(response_json)
        if response_data.get("type", "") != event_type:
            raise ValueError("Event type does not match expected type")
        return response_data.get("event", "")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}") from e
