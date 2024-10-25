"""
Module to manage the chatbot state.
"""

import atexit
import random
import re
import shutil
from datetime import datetime, timedelta, timezone
from typing import List, TypedDict, cast

import civitai
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from jinja2 import Template

import database as db
from model import ChatMessage, Model

MAX_TOKENS = 4096
MAX_NEW_TOKENS = 512


class StampedChatMessage(TypedDict):
    """Chat message type."""

    role: str
    content: str
    timestamp: datetime


class ImageGenerationFailedException(Exception):
    """Exception raised when image generation fails on Civitai's side."""


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
        f"message to {thread['user']}?"
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
        f"The time is currently {now}, and you have decided to send {thread['user']} "
        f"another message. Please write your message to {thread['user']}.\n"
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
        character=character["id"],
        type=event_type,
        content=response["content"],
    )
    db.events.insert_event(event)


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
    # Guard clause to ensure character has an ID
    if "id" not in character:
        raise ValueError("Character does not have an ID.")
    assert character["id"]

    # generate image description
    now = db.convert_dt_ts(datetime.now(timezone.utc))
    sys_message = _get_system_message("photo", character)
    chatlog = Events(character["id"], True, True, True).sorted(
        truncate=True, model=model
    )
    content = (
        f"The time is currently {now}. Please describe "
        "the photo you are about to post.\n"
        "Do not include anything except for the image description."
    )
    chatlog.append(ChatMessage(role="user", content=content))
    description = _generate_text(model, sys_message, chatlog)

    # generate stable diffusion prompt
    sys_message = _get_system_message("sd-prompt", character)
    prompt_chatlog = [ChatMessage(role="user", content=description["content"])]
    prompt = _generate_text(model, sys_message, prompt_chatlog)

    # generate caption
    sys_message = _get_system_message("caption", character, description["content"])
    content = (
        f"The time is currently {now}. The photo description is "
        f"{description['content']}. Please write a caption for the photo.\n"
        "Do not include anything except for the caption."
    )

    chatlog[-1] = ChatMessage(role="user", content=content)
    caption = _generate_text(model, sys_message, chatlog)

    # insert post into database
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
    # guard clause to ensure character has an ID
    if "id" not in character:
        raise ValueError("Character does not have an ID.")
    assert character["id"]

    # generate description
    sys_message = _get_system_message("text_post", character)
    now = db.convert_dt_ts(datetime.now(timezone.utc))
    chatlog = Events(character["id"], True, True, True).sorted(
        truncate=True, model=model
    )
    content = (
        f"The time is currently {now}. Please write "
        "the post you are about to make.\n"
        "Reminder: It is a text only post. "
        "Do not include anything except for the post content."
    )
    chatlog.append(ChatMessage(role="user", content=content))
    description = _generate_text(model, sys_message, chatlog)

    # insert post into database
    post = db.Post(
        character=character["id"],
        description=description["content"],
        image_post=False,
        prompt="",
        caption="",
    )
    db.posts.insert_social_media_post(post)


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

    return ChatMessage(role="system", content=current_content)


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
                    timestamp=message["timestamp"],
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
            self.events = db.events.select_events_by_character(char_id)
        # messages
        self.m_bool = messages
        if messages:
            self.messages = db.select_messages_by_character(char_id)
        # posts
        self.p_bool = posts
        if posts:
            self.posts = db.posts.get_posts_by_character(char_id)

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
                    role="system", content=content, timestamp=event["timestamp"]
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
                    message["thread"],
                    getattr(message["thread"], "user", None),
                ]
            ):
                continue
            assert message["timestamp"]
            assert message["content"]
            assert message["role"]
            assert message["thread"]
            assert message["thread"]["user"]
            if message["role"] == "user":
                content = (
                    f"At time {message['timestamp']}, "
                    f"{message['thread']['user']} sent the message: "
                    f"{message['content']}"
                )

            else:
                content = (
                    f"At time {message['timestamp']}, you sent the "
                    f"message: {message['content']} to {message['thread']['user']}"
                )

            message_log.append(
                StampedChatMessage(
                    role="system",
                    content=content,
                    timestamp=message["timestamp"],
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
                    role="system", content=content, timestamp=post["timestamp"]
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


def schedule_events(model: Model) -> None:
    """Schedule events for the chatbot."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        _scheduled_generation,
        trigger="interval",
        minutes=1,
        args=[model],
    )
    scheduler.start()
    atexit.register(scheduler.shutdown)


def _scheduled_generation(model: Model) -> None:
    """
    Called once a minute and uses internal logic decide what to generate.
    """
    char_ids = db.select_character_ids()
    for char_id in char_ids:
        if random.random() < 1 / 30:
            # Thoughts happen twice an hour on average
            generate_event(model, char_id, "thought")
        if random.random() < 1 / 30:
            # Events happen twice an hour on average
            generate_event(model, char_id, "event")
        if random.random() < 1 / 60:
            # Posts happen once an hour on average
            generate_social_media_post(model, char_id)
