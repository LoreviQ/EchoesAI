"""
Handles the functions required to generate a response from the chatbot.
I.E. Events between a user and a character
"""

from datetime import datetime, timedelta, timezone
from typing import List, cast

import database_old as db

from .events import _turn_message_into_chatmessage
from .main import _generate_text, _get_system_message, _parse_time
from .model import Model
from .types import MAX_TOKENS, ChatMessage, StampedChatMessage


def _create_message_log(
    thread_id: int, model: Model | None = None
) -> List[ChatMessage]:
    chatlog: List[StampedChatMessage] = []
    messages = db.select_messages_by_thread(thread_id)
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
        chatlog.append(_turn_message_into_chatmessage(message))
    chatlog = sorted(chatlog, key=lambda x: x["timestamp"])
    chatlog = [cast(ChatMessage, x) for x in chatlog]
    if not model:
        # if no model is provided, don't truncate and return early
        return chatlog
    truncated_log = chatlog[:]
    while model.token_count(truncated_log) > MAX_TOKENS:
        truncated_log.pop(0)
    return truncated_log


def response_cycle(
    model: Model, thread_id: int, duration: timedelta | None = None
) -> None:
    """
    Handles the entire response cycle for recieving and generating a new message.
    """
    # delete previous scheduled messages
    thread = db.select_thread(thread_id)
    db.delete_scheduled_messages_from_thread(thread_id)
    # get response time
    if duration is None:
        duration = _get_response_time(model, thread)
    timestamp = datetime.now(timezone.utc) + duration
    # get a response from the model
    _get_response_and_submit(model, thread, timestamp)


def _get_response_time(model: Model, thread: db.Thread) -> timedelta:
    assert thread["id"]
    sys_message = _get_system_message("time", thread)
    chatlog = _create_message_log(thread["id"], model=model)
    now = db.convert_dt_ts(datetime.now(timezone.utc))
    user = db.select_user_by_id(thread["user_id"])
    content = (
        f"The time is currently {now}. How long until you next send a "
        f"message to {user['username']}?\n "
        "Reminder to write the time in the format 'nd nh nm ns'."
    )
    chatlog.append(ChatMessage(role="user", content=content))
    response = _generate_text(model, sys_message, chatlog)
    return _parse_time(response["content"])


def _get_response_and_submit(
    model: Model,
    thread: db.Thread,
    timestamp: datetime,
) -> None:
    assert thread["id"]
    sys_message = _get_system_message("chat", thread)
    chatlog = _create_message_log(thread["id"], model=model)
    now = db.convert_dt_ts(datetime.now(timezone.utc))
    user = db.select_user_by_id(thread["user_id"])
    content = (
        f"The time is currently {now}, and you have decided to send {user['username']} "
        f"another message. Please generate message to {user['username']}.\n"
    )
    chatlog.append(
        {
            "role": "user",
            "content": content,
        }
    )
    response = _generate_text(model, sys_message, chatlog)
    message = db.Message(
        thread_id=thread["id"],
        content=response["content"],
        role=response["role"],
        timestamp=db.convert_dt_ts(timestamp),
    )
    db.insert_message(message)
