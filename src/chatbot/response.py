"""
Handles the functions required to generate a response from the chatbot.
I.E. Events between a user and a character
"""

from datetime import datetime, timedelta, timezone
from typing import List, cast

import database as db

from .main import _generate_text, _get_system_message, _parse_time
from .model import Model
from .types import MAX_TOKENS, ChatMessage, StampedChatMessage


class Messages:
    """
    Class to manage messages related to a particular thread.
    """

    def __init__(self, thread_id: int) -> None:
        self.messages = db.select_messages_by_thread(thread_id)

    def _convert_messages_to_chatlog(self) -> List[StampedChatMessage]:
        """
        Convert messages into chatlog messages.
        """
        message_log: List[StampedChatMessage] = []
        for message in self.messages:
            if not all(
                [
                    message["timestamp"],
                    message["content"],
                    message["role"],
                ]
            ):
                continue
            assert message["timestamp"]
            assert message["content"]
            assert message["role"]
            content = f"---{message['timestamp']}---\n{message['content']}"
            message_log.append(
                StampedChatMessage(
                    role=message["role"],
                    content=content,
                    timestamp=db.convert_ts_dt(message["timestamp"]),
                )
            )
        return message_log

    def sorted(
        self, truncate: bool = False, model: Model | None = None
    ) -> List[ChatMessage]:
        """
        Return a sorted log of messages, optionally truncated.
        """
        sorter = self._convert_messages_to_chatlog()
        sorter = sorted(sorter, key=lambda x: x["timestamp"])
        chatlog = [cast(ChatMessage, x) for x in sorter]
        if not truncate:
            return chatlog
        if not model:
            raise ValueError("Model must be provided to truncate chatlog.")
        # truncate chatlog to max tokens
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
    chatlog = Messages(thread["id"]).sorted(truncate=True, model=model)
    now = db.convert_dt_ts(datetime.now(timezone.utc))
    content = (
        f"The time is currently {now}. How long until you next send a "
        f"message to {thread['user_id']}?"
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
    chatlog = Messages(thread["id"]).sorted(truncate=True, model=model)
    now = db.convert_dt_ts(datetime.now(timezone.utc))
    content = (
        f"The time is currently {now}, and you have decided to send {thread['user_id']} "
        f"another message. Please write your message to {thread['user_id']}.\n"
        "Do not include anything except for the message content, such as time or message recipient."
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
