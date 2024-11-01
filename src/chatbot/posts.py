"""
This module contains functions for generating social media posts.
"""

import io
import json
import os
import random
import time
from datetime import datetime, timezone

import civitai
import requests
from google.cloud import storage

import database as db

from .events import _create_complete_event_log
from .main import _generate_text, _get_system_message
from .model import Model
from .types import ChatMessage, ImageGenerationFailedException


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
    now = datetime.now(timezone.utc).isoformat()
    sys_message = _get_system_message("photo", character)
    chatlog = _create_complete_event_log(character["id"], model=model)
    content = f"The time is currently {now}. Generate an image post."
    chatlog.append(ChatMessage(role="user", content=content))
    generated_image = _generate_text(model, sys_message, chatlog)
    description, caption = _parse_response_image_post(generated_image["content"])

    # generate stable diffusion prompt
    sys_message = _get_system_message("sd-prompt", character)
    prompt_chatlog = [ChatMessage(role="user", content=description)]
    prompt = _generate_text(model, sys_message, prompt_chatlog)["content"]

    # insert post into database
    post = db.Post(
        char_id=character["id"],
        content=caption,
        image_post=True,
        image_description=description,
        prompt=prompt,
    )
    post_id = db.posts.insert_post(post)

    # use prompt to generate image
    _civitai_generate_image(character, post_id, prompt)


def _generate_text_post(model: Model, character: db.Character) -> None:
    # guard clause to ensure character has an ID
    if "id" not in character:
        raise ValueError("Character does not have an ID.")
    assert character["id"]

    # generate description
    sys_message = _get_system_message("text_post", character)
    now = datetime.now(timezone.utc).isoformat()
    chatlog = _create_complete_event_log(character["id"], model=model)
    content = f"The time is currently {now}. Generate a text post."
    chatlog.append(ChatMessage(role="user", content=content))
    post_content = _generate_text(model, sys_message, chatlog)["content"]
    post_content = _parse_response_test_post(post_content)

    # insert post into database
    post = db.Post(
        char_id=character["id"],
        content=post_content,
        image_post=False,
    )
    db.posts.insert_post(post)


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


def _parse_response_image_post(response_json: str) -> tuple[str, str]:
    """
    Parses the JSON string from the model response and
    returns the 'image_description' and 'caption' components.
    """
    try:
        response_data = json.loads(response_json)
        return response_data.get("image_description", ""), response_data.get(
            "caption", ""
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}") from e


def _parse_response_test_post(response_json: str) -> str:
    """
    Parses the JSON string from the model response and returns the 'post' component.
    """
    try:
        response_data = json.loads(response_json)
        return response_data.get("post", "")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}") from e
