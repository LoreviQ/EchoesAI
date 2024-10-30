"""
Handles the functions required to generate an event from the chatbot.
I.E. Events only containing the character
"""

from datetime import datetime, timezone
from typing import List, cast

import database as db

from .main import _generate_text, _get_system_message
from .model import Model
from .types import MAX_TOKENS, ChatMessage, StampedChatMessage


class Events:
    """
    Class to manage events for a character.
    """

    def __init__(self, char_id: int, events: bool, messages: bool, posts: bool) -> None:
        if not any([events, messages, posts]):
            raise ValueError("At least one of events, messages, or posts must be True.")
        # events
        self.e_bool = events
        if events:
            self.events = db.events.select_events(db.Event(char_id=char_id))
        # messages
        self.m_bool = messages
        if messages:
            self.messages = db.select_messages_by_character(char_id)
        # posts
        self.p_bool = posts
        if posts:
            self.posts = db.posts.select_posts(db.Post(char_id=char_id))

    def _convert_events_to_chatlog(self) -> List[StampedChatMessage]:
        """
        Convert events into chatlog messages.
        """
        event_log: List[StampedChatMessage] = []
        for event in self.events:
            if not all(
                [
                    event["type"],
                    event["timestamp"],
                    event["content"],
                ]
            ):
                continue
            assert event["type"]
            assert event["timestamp"]
            assert event["content"]
            match event["type"]:
                case "thought":
                    content = (
                        f"At time {event['timestamp']}, you had the "
                        f"following thought: {event['content']}"
                    )
                case "event":
                    content = (
                        f"At time {event['timestamp']}, you were "
                        f"doing the following: {event['content']}"
                    )
            event_log.append(
                StampedChatMessage(
                    role="system",
                    content=content,
                    timestamp=db.convert_ts_dt(event["timestamp"]),
                )
            )
        return event_log

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
                    message["thread_id"],
                ]
            ):
                continue
            assert message["timestamp"]
            assert message["content"]
            assert message["role"]
            assert message["thread_id"]
            if message["role"] == "user":
                content = (
                    f"At time {message['timestamp']}, "
                    f"{message['thread_id']} sent the message: "
                    f"{message['content']}"
                )

            else:
                content = (
                    f"At time {message['timestamp']}, you sent the "
                    f"message: {message['content']} to {message['thread_id']}"
                )

            message_log.append(
                StampedChatMessage(
                    role="system",
                    content=content,
                    timestamp=db.convert_ts_dt(message["timestamp"]),
                )
            )
        return message_log

    def _convert_posts_to_chatlog(self) -> List[StampedChatMessage]:
        """
        Convert posts into chatlog messages.
        """
        post_log: List[StampedChatMessage] = []
        for post in self.posts:
            if post["image_post"]:
                if not all(
                    [
                        post["caption"],
                        post["timestamp"],
                        post["description"],
                    ]
                ):
                    continue
                assert post["caption"]
                assert post["timestamp"]
                assert post["description"]
                content = (
                    f"At time {post['timestamp']}, you posted the following "
                    f"photo to social media: {post['description']} with the caption: "
                    f"{post['caption']}"
                )
            else:
                if not all(
                    [
                        post["timestamp"],
                        post["description"],
                    ]
                ):
                    continue
                assert post["timestamp"]
                assert post["description"]
                content = (
                    f"At time {post['timestamp']}, you posted the following "
                    f"to social media:\n{post['description']}"
                )
            post_log.append(
                StampedChatMessage(
                    role="system",
                    content=content,
                    timestamp=db.convert_ts_dt(post["timestamp"]),
                )
            )
        return post_log

    def sorted(
        self, truncate: bool = False, model: Model | None = None
    ) -> List[ChatMessage]:
        """
        Return a sorted log of all events, messages, and posts, optionally truncated.
        """
        sorter: List[StampedChatMessage] = []
        if self.e_bool:
            sorter += self._convert_events_to_chatlog()
        if self.m_bool:
            sorter += self._convert_messages_to_chatlog()
        if self.p_bool:
            sorter += self._convert_posts_to_chatlog()
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


def generate_event(model: Model, character_id: int, event_type: str) -> None:
    """
    Generate an event message.
    """
    character = db.select_character_by_id(character_id)
    sys_message = _get_system_message(event_type, character)
    chatlog = Events(character_id, True, True, True).sorted(truncate=True, model=model)
    timestamp = db.convert_dt_ts(datetime.now(timezone.utc))
    match event_type:
        case "thought":
            content = f"The time is currently {timestamp}. Please write your current thoughts."
        case "event":
            content = (
                f"The time is currently {timestamp}. "
                "Please describe what you are currently doing.\n"
                "Do not include anything except for the event description."
            )

    chatlog.append(ChatMessage(role="user", content=content))
    response = _generate_text(model, sys_message, chatlog)
    event = db.Event(
        char_id=character["id"],
        type=event_type,
        content=response["content"],
    )
    db.events.insert_event(event)
