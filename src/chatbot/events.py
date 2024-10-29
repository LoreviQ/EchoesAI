"""
Handles the functions required to generate an event from the chatbot.
I.E. Events only containing the character
"""

import io
import os
import random
import time
from datetime import datetime, timezone
from typing import List, cast

import civitai
import requests
from google.cloud import storage

import database as db

from .main import _generate_text, _get_system_message
from .model import Model
from .types import (
    MAX_TOKENS,
    ChatMessage,
    ImageGenerationFailedException,
    StampedChatMessage,
)


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


def generate_social_media_post(model: Model, character_id: int) -> None:
    """
    Generate a social media post.
    """
    character = db.select_character_by_id(character_id)
    # even if image posts are allowed, there is a 2/3 chance of generating a text post
    if not character["img_gen"] or random.random() < 2 / 3:
        return _generate_text_post(model, character)
    return _generate_image_post(model, character)


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
        char_id=character["id"],
        description=description["content"],
        image_post=True,
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
        char_id=character["id"],
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
    try:
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    except KeyError as exc:
        raise ValueError(
            "GOOGLE_APPLICATION_CREDENTIALS environment variable not set."
        ) from exc
    if "model" not in character:
        raise ValueError("Character does not have a model specified.")
    assert character["name"]
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
        while _check_civitai_for_image(
            response["token"], character["name"].lower(), post_id
        ):
            time.sleep(60)
    except requests.exceptions.RequestException as e:
        raise IOError("Failed to download image from provided URL.") from e
    except IOError as e:
        raise IOError("Failed to save the downloaded image.") from e


def _check_civitai_for_image(token: str, char_name: str, post_id: int) -> bool:
    response = civitai.jobs.get(token=token)
    # if image is available, download it
    if response["jobs"][0]["result"]["available"]:
        url = response["jobs"][0]["result"]["blobUrl"]
        image_r = requests.get(url, stream=True, timeout=5)
        image_r.raise_for_status()  # Raise an HTTPError for bad resposne
        destination_blob_name = f"{char_name}/posts/{post_id}.jpg"
        image_stream = io.BytesIO(image_r.content)
        _upload_image_to_gcs(image_stream, destination_blob_name)
        db.posts.update_post_with_image_path(
            post_id,
            destination_blob_name,
        )
        return False
    # if image is not available and not scheduled, raise an exception
    if not response["jobs"][0]["scheduled"]:
        raise ImageGenerationFailedException(
            "Image generation failed on Civitai's side."
        )
    # if image is not available but scheduled, return True to continue checking
    return True


def _upload_image_to_gcs(image_stream: io.BytesIO, destination_blob_name: str) -> None:
    """Uploads an image to a GCS bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket("echoesai-public-images")
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(image_stream, rewind=True)
