"""
Module to manage the chatbot state.
"""

import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Tuple, Union

import civitai
from jinja2 import Template

from database import DB, Event, Message, Thread, convert_dt_ts
from model import Model

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
        "photo": lambda timestamp: f"The time is currently {timestamp}. Please describe the photo you are about to post.",
        "caption": lambda timestamp, p_desc: f"The time is currently {timestamp}. The photo description is {p_desc}. Please write a caption for the photo.",
    },
}


class Chatbot:
    """
    Class to manage a chatbot state.
    """

    def __init__(
        self,
        character: str,
        database: DB,
        model: Model,
    ) -> None:
        self.database = database
        self.model = model
        self.character = character
        with open(f"characters/{self.character}.json", "r", encoding="utf-8") as file:
            self.character_info = json.load(file)

    def get_system_message(
        self,
        system_type: str,
        thread: Thread | None = None,
        photo_description: str = "",
    ) -> List[Dict[str, str]]:
        """
        Change the system message between several preconfigured options.
        """
        with open(f"templates/{system_type}.txt", "r", encoding="utf-8") as file:
            template_content = file.read()

        # prepare context for rendering
        context = {
            "char": self.character_info["char"],
            "description": self.character_info["description"],
            "age": self.character_info["age"],
            "height": self.character_info["height"],
            "personality": self.character_info["personality"],
            "appearance": self.character_info["appearance"],
            "loves": self.character_info["loves"],
            "hates": self.character_info["hates"],
            "details": self.character_info["details"],
            "scenario": self.character_info["scenario"],
            "important": self.character_info["important"],
            "photo_description": photo_description,
        }
        if thread:
            phase = thread["phase"]
            context["user"] = thread["user"]
            context["phase_name"] = self.character_info["phases"][phase]["name"]
            context["phase_description"] = self.character_info["phases"][phase][
                "description"
            ]
            context["phase_response"] = self.character_info["phases"][phase]["response"]
            context["phase_names"] = self.character_info["phases"][phase]["names"]
            context["phase_advance"] = self.character_info["phases"][phase]["advance"]

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

    def _generate_text(
        self, system_message: List[Dict[str, str]], chat: List[Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Generate a response from the chatbot.
        """
        return self.model.generate_response(system_message + chat, max_new_tokens=512)

    def response_cycle(self, thread_id: int, duration: timedelta | None = None) -> None:
        """
        Handles the entire response cycle for recieving and generating a new message.
        """
        # delete previous scheduled messages
        thread = self.database.get_thread(thread_id)
        self.database.delete_scheduled_messages_from_thread(thread_id)
        # get response time
        if duration is None:
            duration = self._get_response_time(thread)
        timestamp = datetime.now(timezone.utc) + duration
        # get a response from the model
        self._get_response_and_submit(thread, timestamp)

    def _get_response_time(self, thread: Thread) -> timedelta:
        sys_message = self.get_system_message("time", thread)
        messages = self.database.get_messages_by_thread(thread["id"])
        chatlog = self._convert_messages_to_chatlog(messages)
        chatlog.append(
            {
                "role": "user",
                "content": messageTemplates["tt_next_message"](
                    convert_dt_ts(datetime.now(timezone.utc)),
                    thread["user"],
                ),
            }
        )
        response = self._generate_text(sys_message, chatlog)
        return _parse_time(response["content"])

    def _get_response_and_submit(self, thread: Thread, timestamp: datetime) -> None:
        sys_message = self.get_system_message("chat", thread)
        messages = self.database.get_messages_by_thread(thread["id"])
        chatlog = self._convert_messages_to_chatlog(messages)
        chatlog.append(
            {
                "role": "user",
                "content": messageTemplates["get_message"](
                    convert_dt_ts(datetime.now(timezone.utc)),
                    thread["user"],
                ),
            }
        )
        response = self._generate_text(sys_message, chatlog)
        self.database.post_message(
            thread["id"], response["content"], response["role"], timestamp
        )

    def generate_event(self, event_type: str) -> None:
        """
        Generate an event message.
        """
        sys_message = self.get_system_message(event_type)
        chatlog = self._event_chatlog()
        chatlog.append(
            {
                "role": "user",
                "content": messageTemplates["get_event"][event_type](
                    convert_dt_ts(datetime.now(timezone.utc))
                ),
            }
        )
        response = self._generate_text(sys_message, chatlog)
        self.database.post_event(self.character, event_type, response["content"])

    def _event_chatlog(self) -> List[Dict[str, str]]:
        """
        Create a custom chatlog of events for the chatbot.
        """
        events = self.database.get_events_by_chatbot(self.character)
        messages = self.database.get_messages_by_character(self.character)
        all_events = _combine_events(("events", events), ("messages", messages))
        chatlog = []
        for event in all_events:
            match event["type"]:
                case "events":
                    chatlog.append(
                        {
                            "role": "user",
                            "content": messageTemplates["events"](
                                event["timestamp"], event["value"]["content"]
                            ),
                        }
                    )
                case "thoughts":
                    chatlog.append(
                        {
                            "role": "user",
                            "content": messageTemplates["thoughts"](
                                event["timestamp"], event["value"]["content"]
                            ),
                        }
                    )
                case "messages":
                    if event["value"]["role"] == "user":
                        chatlog.append(
                            {
                                "role": "user",
                                "content": messageTemplates["message_received"](
                                    event["timestamp"],
                                    event["value"]["content"],
                                    event["value"]["user"],
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
                                    event["value"]["user"],
                                ),
                            }
                        )
        return chatlog

    def generate_social_media_post(self) -> None:
        """
        Generate a social media post.
        """
        # generate image description
        sys_message = self.get_system_message("photo")
        chatlog = self._event_chatlog()
        chatlog.append(
            {
                "role": "user",
                "content": messageTemplates["get_post"]["photo"](
                    convert_dt_ts(datetime.now(timezone.utc))
                ),
            }
        )
        description = self._generate_text(sys_message, chatlog)

        # generate stable diffusion prompt
        sys_message = self.get_system_message("sd-prompt")
        prompt = [
            {
                "role": "user",
                "content": description["content"],
            }
        ]
        prompt = self._generate_text(sys_message, prompt)

        # use prompt to generate image
        self.civitai_generate_image(prompt["content"])

        # generate caption
        sys_message = self.get_system_message("caption")
        chatlog[-1]["content"] = messageTemplates["get_post"]["caption"](
            convert_dt_ts(datetime.now(timezone.utc)), description["content"]
        )
        caption = self._generate_text(sys_message, chatlog)

    def _convert_messages_to_chatlog(
        self, messages: List[Message]
    ) -> List[Dict[str, str]]:
        chatlog: List[Dict[str, str]] = []
        for message in messages:
            formatter: Callable
            if message["role"] == "user":
                formatter = messageTemplates["message_received"]
            else:
                formatter = messageTemplates["message_sent"]
            chatlog.append(
                {
                    "role": message["role"],
                    "content": formatter(
                        convert_dt_ts(message["timestamp"]),
                        message["content"],
                        message["user"],
                    ),
                }
            )
        return chatlog

    def civitai_generate_image(self, prompt) -> None:
        """
        Generate an image using the Civitai API.
        """
        civitai_input = {
            "model": self.character_info["model"],
            "params": {
                "prompt": self.character_info["img_gen"]["global_positive"]
                + self.character_info["appearance"]
                + prompt,
                "negativePrompt": self.character_info["img_gen"]["global_negative"],
                "scheduler": "EulerA",
                "steps": 29,
                "cfgScale": 5,
                "width": 1024,
                "height": 1024,
                "clipSkip": 1,
            },
            "additionalNetworks": {
                self.character_info["img_gen"]["additional_networks"]
            },
        }
        response = civitai.image.create(civitai_input)
        # TODO: save image to database


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
    *event_lists: Tuple[str, Union[List[Event], List[Message]]]
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
                    event_type = event["type"]
                case "messages":
                    event_type = "messages"
            result.append(
                {
                    "type": event_type,
                    "timestamp": event["timestamp"],
                    "value": event,
                }
            )
    return sorted(result, key=lambda x: x["timestamp"])
