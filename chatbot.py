"""
Module to manage the chatbot state.
"""

import random
import re
import shutil
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Tuple, Union, cast

import civitai
import requests
from jinja2 import Template

import database as db
from model import Model

MAX_TOKENS = 4096

messageTemplates: Dict[str, Any] = {
    "tt_next_message": lambda timestamp, user: f"The time is currently {timestamp}. How long until you next send a message to {user}?",
    "get_message": lambda timestamp, user: f"The time is currently {timestamp}, and you have decided to send {user} another message. Please write your message to {user}. Do not include the time in your response.",
    "message_sent": lambda timestamp, message, user: f"At time {timestamp}, you sent the following message to {user}:\n{message}",
    "message_received": lambda timestamp, message, user: f"At time {timestamp}, you received the following message from {user}:\n{message}",
    "events": lambda timestamp, event: f"At time {timestamp}, you were doing the following:\n{event}",
    "thoughts": lambda timestamp, thought: f"At time {timestamp}, you had the following thought:\n{thought}",
    "get_event": {
        "event": lambda timestamp: f"The time is currently {timestamp}. Please describe what you are doing now.",
        "thought": lambda timestamp: f"The time is currently {timestamp}. Please write your current thoughts.",
    },
    "get_post": {
        "text": lambda timestamp: f"The time is currently {timestamp}. Please write the post you are about to make.",
        "photo": lambda timestamp: f"The time is currently {timestamp}. Please describe the photo you are about to post.",
        "caption": lambda timestamp, p_desc: f"The time is currently {timestamp}. The photo description is {p_desc}. Please write a caption for the photo.",
    },
}


class ImageGenerationFailedException(Exception):
    """Exception raised when image generation fails on Civitai's side."""


def _generate_text(
    model: Model,
    system_message: List[Dict[str, str]],
    chat: List[Dict[str, str]],
) -> Dict[str, str]:
    """
    Generate a response from the chatbot.
    """
    return model.generate_response(system_message + chat, max_new_tokens=512)


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
    messages = db.select_messages_by_thread(thread["id"])
    chatlog = _convert_messages_to_chatlog(messages)
    chatlog.append(
        {
            "role": "user",
            "content": messageTemplates["tt_next_message"](
                db.convert_dt_ts(datetime.now(timezone.utc)),
                thread["user"],
            ),
        }
    )
    response = _generate_text(model, sys_message, chatlog)
    return _parse_time(response["content"])


def _get_response_and_submit(
    model: Model,
    thread: db.Thread,
    timestamp: datetime,
) -> None:
    assert thread["id"]
    sys_message = _get_system_message("chat", thread)
    messages = db.select_messages_by_thread(thread["id"])
    chatlog = _convert_messages_to_chatlog(messages)
    chatlog.append(
        {
            "role": "user",
            "content": messageTemplates["get_message"](
                db.convert_dt_ts(datetime.now(timezone.utc)),
                thread["user"],
            ),
        }
    )
    response = _generate_text(model, sys_message, chatlog)
    message = db.Message(
        thread=thread,
        content=response["content"],
        role=response["role"],
        timestamp=timestamp,
    )
    db.insert_message(message)


def generate_event(model: Model, character_id: int, event_type: str) -> None:
    """
    Generate an event message.
    """
    character = db.select_character(character_id)
    sys_message = _get_system_message(event_type, character)
    chatlog = _event_log(model, character)
    chatlog.append(
        {
            "role": "user",
            "content": messageTemplates["get_event"][event_type](
                db.convert_dt_ts(datetime.now(timezone.utc))
            ),
        }
    )
    response = _generate_text(model, sys_message, chatlog)
    event = db.Event(
        character=character["id"],
        type=event_type,
        content=response["content"],
    )
    db.events.insert_event(event)


def _event_log(model: Model, character: db.Character) -> List[Dict[str, str]]:
    """
    Create a custom chatlog of events for the chatbot.
    """
    assert character["id"]
    events = db.events.select_events_by_character(character["id"])
    messages = db.select_messages_by_character(character["id"])
    all_events = _combine_events(("events", events), ("messages", messages))
    chatlog = []
    for event in all_events:
        match event["type"]:
            case "event":
                chatlog.append(
                    {
                        "role": "user",
                        "content": messageTemplates["events"](
                            event["timestamp"], event["value"]["content"]
                        ),
                    }
                )
            case "thought":
                chatlog.append(
                    {
                        "role": "user",
                        "content": messageTemplates["thoughts"](
                            event["timestamp"], event["value"]["content"]
                        ),
                    }
                )
            case "message":
                if event["value"]["role"] == "user":
                    chatlog.append(
                        {
                            "role": "user",
                            "content": messageTemplates["message_received"](
                                event["timestamp"],
                                event["value"]["content"],
                                event["value"]["thread"]["user"],
                            ),
                        }
                    )
                else:
                    chatlog.append(
                        {
                            "role": "user",
                            "content": messageTemplates["message_sent"](
                                event["timestamp"],
                                event["value"]["content"],
                                event["value"]["thread"]["user"],
                            ),
                        }
                    )
    truncated_log = chatlog[:]
    while model.token_count(truncated_log) > MAX_TOKENS:
        truncated_log.pop(0)
    return truncated_log


def generate_social_media_post(model: Model, character_id: int) -> None:
    """
    Generate a social media post.
    """
    character = db.select_character(character_id)
    # even if image posts are allowed, there is a 2/3 chance of generating a text post
    if character["img_gen"] is not True or random.random() < 2 / 3:
        _generate_text_post(model, character)
    _generate_image_post(model, character)


def _generate_image_post(model: Model, character: db.Character) -> None:
    """
    Generate a social media post with an image.
    """
    # generate image description
    sys_message = _get_system_message("photo", character)
    chatlog = _event_log(model, character)
    chatlog.append(
        {
            "role": "user",
            "content": messageTemplates["get_post"]["photo"](
                db.convert_dt_ts(datetime.now(timezone.utc))
            ),
        }
    )
    description = _generate_text(model, sys_message, chatlog)

    # generate stable diffusion prompt
    sys_message = _get_system_message("sd-prompt", character)
    prompt_chatlog = [
        {
            "role": "user",
            "content": description["content"],
        }
    ]
    prompt = _generate_text(model, sys_message, prompt_chatlog)

    # generate caption
    sys_message = _get_system_message("caption", character, description["content"])
    chatlog[-1]["content"] = messageTemplates["get_post"]["caption"](
        db.convert_dt_ts(datetime.now(timezone.utc)), description["content"]
    )
    caption = _generate_text(model, sys_message, chatlog)
    post = db.Post(
        character=character["id"],
        description=description["content"],
        prompt=prompt["content"],
        caption=caption["content"],
    )
    post_id = db.posts.insert_social_media_post(post)

    # use prompt to generate image
    _civitai_generate_image(character, post_id, prompt["content"])


def _generate_text_post(model: Model, character: db.Character) -> None:
    # generate description
    sys_message = _get_system_message("text_post", character)
    chatlog = _event_log(model, character)
    chatlog.append(
        {
            "role": "user",
            "content": messageTemplates["get_post"]["text"](
                db.convert_dt_ts(datetime.now(timezone.utc))
            ),
        }
    )
    description = _generate_text(model, sys_message, chatlog)
    post = db.Post(
        character=character["id"],
        description=description["content"],
        image_post=False,
        prompt="",
        caption="",
    )
    db.posts.insert_social_media_post(post)


def _convert_messages_to_chatlog(
    messages: List[db.Message],
) -> List[Dict[str, str]]:
    chatlog: List[Dict[str, str]] = []
    for message in messages:
        formatter: Callable
        assert message["role"]
        assert message["thread"]
        if message["role"] == "user":
            formatter = messageTemplates["message_received"]
        else:
            formatter = messageTemplates["message_sent"]
        chatlog.append(
            {
                "role": message["role"],
                "content": formatter(
                    db.convert_dt_ts(message["timestamp"]),
                    message["content"],
                    message["thread"]["user"],
                ),
            }
        )
    return chatlog


def _civitai_generate_image(character: db.Character, post_id: int, prompt: str) -> None:
    """
    Generate an image using the Civitai API.
    """
    if "model" not in character:
        raise ValueError("Character does not have a model specified.")
    assert character["name"]
    char_name = character["name"].lower()
    civitai_input = {
        "model": character["model"],
        "params": {
            "prompt": str(character.get("global_positive", ""))
            + str(character.get("appearance", ""))
            + prompt,
            "negativePrompt": character.get("global_negative", ""),
            "scheduler": "EulerA",
            "steps": 15,
            "cfgScale": 5,
            "width": 1024,
            "height": 1024,
        },
        # TODO: Add support for additional networks
    }
    # Handle response from Civitai
    response = civitai.image.create(civitai_input)
    try:
        while True:
            response = civitai.jobs.get(token=response["token"])
            if response["jobs"][0]["result"]["available"]:
                url = response["jobs"][0]["result"]["blobUrl"]
                image_r = requests.get(url, stream=True, timeout=5)
                image_r.raise_for_status()  # Raise an HTTPError for bad resposne
                with open(
                    f"static/images/{char_name}/posts/{post_id}.jpg",
                    "wb",
                ) as out_file:
                    image_r.raw.decode_content = True
                    shutil.copyfileobj(image_r.raw, out_file)
                db.posts.add_image_path_to_post(
                    post_id,
                    f"{char_name}/posts/{post_id}.jpg",
                )
                break
            if not response["jobs"][0]["scheduled"]:
                raise ImageGenerationFailedException(
                    "Image generation failed on Civitai's side."
                )
    except requests.exceptions.RequestException as e:
        print(url)
        raise IOError("Failed to download image from provided URL.") from e
    except IOError as e:
        raise IOError("Failed to save the downloaded image.") from e


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


def _combine_events(
    *event_lists: Tuple[str, Union[List[db.Event], List[db.Message]]]
) -> List[Dict[str, Any]]:
    """
    Creates a compiled event list from multiple sources
    """
    result = []
    for event_list in event_lists:
        for event in event_list[1]:
            event_type: str
            match event_list[0]:
                case "events":
                    event = cast(db.Event, event)
                    assert event["type"]
                    event_type = event["type"]
                case "messages":
                    event_type = "message"
            result.append(
                {
                    "type": event_type,
                    "timestamp": event["timestamp"],
                    "value": event,
                }
            )
    return sorted(result, key=lambda x: x["timestamp"])


def _get_system_message(
    system_type: str,
    data: db.Character | db.Thread,
    photo_description: str = "",
) -> List[Dict[str, str]]:
    """
    Change the system message between several preconfigured options.
    """
    with open(f"templates/{system_type}.txt", "r", encoding="utf-8") as file:
        template_content = file.read()

    if (
        "started" in data
    ):  # Is a thread. TypedDicts apparently don't support type checking. Almost makes you wonder wtf the point of them is.
        thread = cast(db.Thread, data)
        assert thread["character"]
        character = db.select_character(thread["character"])
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
        context["user"] = thread["user"]
        # TODO: Phase-specific messages

    # Render the template until no more changes are detected
    previous_content = None
    current_content = template_content
    while previous_content != current_content:
        previous_content = current_content
        template = Template(current_content)
        current_content = template.render(context)

    return [
        {
            "role": "system",
            "content": current_content,
        }
    ]
