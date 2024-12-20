"""
Handles the functions required to generate a response from the chatbot.
I.E. Events between a user and a character
"""

import json
from datetime import datetime, timedelta, timezone
from typing import List, cast

import database as db

from .events import _message_to_chatmessage
from .main import _generate_text, _get_system_message, _parse_time
from .model import Model
from .types import MAX_TOKENS, ChatMessage, StampedChatMessage


def _create_message_log(
    thread_id: int, model: Model | None = None
) -> List[ChatMessage]:
    chatlog: List[StampedChatMessage] = []
    messages = db.select_messages(db.Message(thread_id=thread_id))
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
        chatlog.append(_message_to_chatmessage(message))
    chatlog = sorted(chatlog, key=lambda x: x["timestamp"])
    sorted_chatlog = [cast(ChatMessage, x) for x in chatlog]
    if not model:
        # if no model is provided, don't truncate and return early
        return sorted_chatlog
    truncated_log = sorted_chatlog[:]
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
    db.delete_scheduled_messages(thread_id)
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
    now = datetime.now(timezone.utc).isoformat()
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
    now = datetime.now(timezone.utc).isoformat()
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
    response = _prompt_model_for_message_response(model, sys_message, chatlog)
    message = db.Message(
        thread_id=thread["id"],
        content=response,
        role="assistant",
        timestamp=timestamp,
    )
    db.insert_message(message)


def _prompt_model_for_message_response(
    model: Model, sys_message: ChatMessage, chatlog: List[ChatMessage]
) -> str:
    """
    Continue to prompt the model to generate a response until a
    valid response is received or the retry limit is reached
    """
    max_retries = 5
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = _generate_text(model, sys_message, chatlog)
            content = _parse_response_message(response["content"])
            break  # Break out of the retry loop if the response is valid
        except ValueError as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise e  # Re-raise the last exception if the retry limit is reached
    return content


def _parse_response_message(response_json: str) -> str:
    """
    Parses the JSON string from the model response and returns the 'message' component.
    """
    try:
        response_data = json.loads(response_json)
        return response_data.get("message", "")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}") from e
