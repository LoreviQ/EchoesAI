"""Utility functions for the chatbot package."""

import re
from datetime import timedelta
from typing import List, cast

from jinja2 import Template

import database as db

from .model import Model
from .types import MAX_NEW_TOKENS, ChatMessage


def _generate_text(
    model: Model,
    system_message: ChatMessage,
    chat: List[ChatMessage],
) -> ChatMessage:
    """
    Generate a response from the chatbot.
    """
    response = model.generate_response(
        [system_message] + chat, max_new_tokens=MAX_NEW_TOKENS
    )
    return cast(ChatMessage, response)


def _get_system_message(
    system_type: str,
    data: db.Character | db.Thread,
    photo_description: str = "",
) -> ChatMessage:
    """
    Change the system message between several preconfigured options.
    """
    with open(f"templates/{system_type}.txt", "r", encoding="utf-8") as file:
        template_content = file.read()

    if "started" in data:  # Is a thread.
        # TypedDicts apparently don't support type checking.
        # Almost makes you wonder wtf the point of them is.
        thread = cast(db.Thread, data)
        assert thread["char_id"]
        character = db.select_character_by_id(thread["char_id"])
    else:
        character = cast(db.Character, data)
        thread = None

    # prepare context for rendering
    context = {
        "char": character.get("name", ""),
        "description": character.get("description", ""),
        "age": character.get("age", ""),
        "height": character.get("height", ""),
        "personality": character.get("personality", ""),
        "appearance": character.get("appearance", ""),
        "loves": character.get("loves", ""),
        "hates": character.get("hates", ""),
        "details": character.get("details", ""),
        "scenario": character.get("scenario", ""),
        "important": character.get("important", ""),
        "photo_description": photo_description,
    }
    if thread:
        user = db.select_user_by_id(thread["user_id"])
        context["user"] = user["username"]
        # TODO: Phase-specific messages

    # Render the template until no more changes are detected
    previous_content = None
    current_content = template_content
    while previous_content != current_content:
        previous_content = current_content
        template = Template(current_content)
        current_content = template.render(context)

    return ChatMessage(role="system", content=current_content)


def _parse_time(time: str) -> timedelta:
    """
    Parse a time string into days, hours, minutes, and seconds.
    """
    days = hours = minutes = seconds = 0
    # regex patterns
    day_pattern = r"(\d+)d"
    hour_pattern = r"(\d+)h"
    minute_pattern = r"(\d+)m"
    second_pattern = r"(\d+)s"

    # Search for the first occurrence of each time unit
    day_match = re.search(day_pattern, time)
    hour_match = re.search(hour_pattern, time)
    minute_match = re.search(minute_pattern, time)
    second_match = re.search(second_pattern, time)

    # Extract the time values
    if day_match:
        days = int(day_match.group(1))
    if hour_match:
        hours = int(hour_match.group(1))
    if minute_match:
        minutes = int(minute_match.group(1))
    if second_match:
        seconds = int(second_match.group(1))

    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
