"""
This module contains functions for generating comments.
"""

import json
from datetime import datetime, timezone
from typing import List, cast

import database as db

from .events import (
    _add_events_to_log,
    _add_posts_to_log,
    _create_complete_event_log,
    _post_to_chatmessage,
    _sort_and_truncate,
)
from .main import _generate_text, _get_system_message
from .model import Model
from .types import ChatMessage, StampedChatMessage


def _chatlog_between_characters(
    primary_char_id: int, secondary_char_id: int, model: Model | None = None
) -> List[ChatMessage]:
    """Generates an event log between two characters."""
    chatlog: List[StampedChatMessage] = []
    _add_events_to_log(primary_char_id, chatlog)
    _add_posts_to_log(chatlog, primary_char_id)
    _add_posts_to_log(chatlog, secondary_char_id)
    return _sort_and_truncate(chatlog, model)


def generate_comment(model: Model, char_id: int) -> None:
    """Full logic for generating a comment."""
    character = db.select_character_by_id(char_id)
    post = _get_post_to_comment_on(character, model)
    comment_content = _generate_comment_content(character, post, model)
    db.insert_comment(
        db.Comment(
            char_id=character["id"],
            post_id=post["id"],
            content=comment_content,
        )
    )


def _get_post_to_comment_on(
    character: db.Character, model: Model | None = None
) -> db.Post:
    """
    Generates the required chatlog for the comment choice step and returns the post to comment on.
    """
    sys_message = _get_system_message("comment_choice", character)
    chatlog = _create_complete_event_log(
        character["id"], events=False, messages=False, posts=True, model=model
    )
    content = (
        "Choose a post to comment on. Respond with a json object with the "
        'post ID. For exmaple: {"postID": 1}'
    )
    chatlog.append(ChatMessage(role="user", content=content))
    response = _generate_text(model, sys_message, chatlog)
    post_id = _parse_response_post_id(response["content"])
    return db.select_post(post_id)


def _parse_response_post_id(response_json: str) -> int:
    """
    Parses the JSON string from the model response and returns the 'postID' component.
    """
    try:
        response_data = json.loads(response_json)
        return int(response_data.get("postID"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}") from e


def _generate_comment_content(
    character: db.Character, post: db.Post, model: Model
) -> str:
    sys_message = _get_system_message("comment_content", character)
    now = datetime.now(timezone.utc).isoformat()
    chatlog = _chatlog_between_characters(character["id"], post["char_id"], model)
    content = "You've decided to comment on the following post:"
    chatlog.append(ChatMessage(role="user", content=content))
    chatlog.append(cast(ChatMessage, _post_to_chatmessage(post)))
    content = f"The time is now {now}, what will you comment? Respond with a json object with the comment content."
    chatlog.append(ChatMessage(role="user", content=content))
    response = _generate_text(model, sys_message, chatlog)
    return _parse_response_comment_content(response["content"])


def _parse_response_comment_content(response_json: str) -> str:
    """
    Parses the JSON string from the model response and returns the 'comment' component.
    """
    try:
        response_data = json.loads(response_json)
        return response_data.get("comment", "")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}") from e
