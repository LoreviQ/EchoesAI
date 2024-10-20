"""
Module to manage the chatbot state.
"""

import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Tuple, Union

from jinja2 import Template

from database import DB, Event, Message, convert_dt_ts
from model import Model

messageTemplates: Dict[str, Any] = {
    "time_to_respond": lambda timestamp: f"The time is currently {timestamp}. How long until you next send a message?",
    "describe_event_now": lambda timestamp: f"The time is currently {timestamp}. Please describe what you are doing now.",
    "event_for_events": lambda timestamp, event: f"At time {timestamp}, you were doing the following:\n{event}",
    "thought_for_events": lambda timestamp, thought: f"At time {timestamp}, you had the following thought:\n{thought}",
    "message_sent_for_events": lambda timestamp, message, user: f"At time {timestamp}, you sent the following message to {user}:\n{message}",
    "message_received_for_events": lambda timestamp, message, user: f"At time {timestamp}, you received the following message from {user}:\n{message}",
}


class Chatbot:
    """
    Class to manage a chatbot state.
    """

    def __init__(
        self,
        thread_id: int,
        database: DB,
        model: Model,
    ) -> None:
        thread = database.get_thread(thread_id)
        self.thread = thread["id"]
        self.database = database
        self.model = model
        self.username = thread["user"]
        self.character = thread["chatbot"]
        self.phase = thread["phase"]
        with open(f"characters/{self.character}.json", "r", encoding="utf-8") as file:
            self.character_info = json.load(file)

    def get_system_message(self, system_type: str) -> List[Dict[str, str]]:
        """
        Change the system message between several preconfigured options.
        """
        with open(f"templates/{system_type}.txt", "r", encoding="utf-8") as file:
            template_content = file.read()

        # prepare context for rendering
        context = {
            "user": self.username,
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
            "phase_name": self.character_info["phases"][self.phase]["name"],
            "phase_description": self.character_info["phases"][self.phase][
                "description"
            ],
            "phase_response": self.character_info["phases"][self.phase]["response"],
            "phase_names": self.character_info["phases"][self.phase]["names"],
            "phase_advance": self.character_info["phases"][self.phase]["advance"],
        }

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

    def _get_response_time(self) -> timedelta:
        sys_message = self.get_system_message("time")
        messages = self.database.get_messages_by_thread(self.thread)
        chatlog: List[Dict[str, str]] = []
        for message in messages:
            formatter: Callable
            if message["role"] == "user":
                formatter = messageTemplates["message_received_for_events"]
            else:
                formatter = messageTemplates["message_sent_for_events"]
            chatlog.append(
                {
                    "role": message["role"],
                    "content": formatter(
                        convert_dt_ts(message["timestamp"]),
                        message["content"],
                        self.username,
                    ),
                }
            )
        chatlog.append(
            {
                "role": "user",
                "content": messageTemplates["time_to_respond"](
                    convert_dt_ts(datetime.now(timezone.utc))
                ),
            }
        )
        response = self._generate_text(sys_message, chatlog)
        return _parse_time(response["content"])

    def _get_response_and_submit(self, timestamp: datetime) -> None:
        sys_message = self.get_system_message("chat")
        messages = self.database.get_messages_by_thread(self.thread)
        chatlog = _convert_messages_to_chatlog(messages)
        response = self._generate_text(sys_message, chatlog)
        self.database.post_message(
            self.thread, response["content"], response["role"], timestamp
        )

    def response_cycle(self, duration: timedelta | None = None) -> None:
        """
        Handles the entire response cycle for recieving and generating a new message.
        """
        # TODO: Check if there's an existing schedulded response and use that to determine the response time
        # get response time
        if duration is None:
            duration = self._get_response_time()
        timestamp = datetime.now(timezone.utc) + duration
        # get a response from the model
        self._get_response_and_submit(timestamp)

    def generate_event(self, event_type: str) -> None:
        """
        Generate an event message.
        """
        sys_message = self.get_system_message(event_type)
        events = self.database.get_events_by_type_and_chatbot("event", self.character)
        thoughts = self.database.get_events_by_type_and_chatbot(
            "thought", self.character
        )
        messages = self.database.get_messages_by_thread(self.thread)
        all_events = self._combine_events(
            ("events", events), ("thoughts", thoughts), ("messages", messages)
        )
        custom_chatlog = self._event_chatlog(all_events)
        response = self._generate_text(sys_message, custom_chatlog)
        self.database.post_event(self.character, event_type, response["content"])

    def _combine_events(
        self, *event_lists: Tuple[str, Union[List[Event], List[Message]]]
    ) -> List[Dict[str, Any]]:
        result = []
        for event_list in event_lists:
            for event in event_list[1]:
                result.append(
                    {
                        "type": event_list[0],
                        "timestamp": event["timestamp"],
                        "value": event,
                    }
                )
        return sorted(result, key=lambda x: x["timestamp"])

    def _event_chatlog(self, events: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Create a custom chatlog of events for the chatbot.
        """
        chatlog = []
        for event in events:
            match event["type"]:
                case "events":
                    chatlog.append(
                        {
                            "role": "user",
                            "content": messageTemplates["event_for_events"](
                                event["timestamp"], event["value"]["content"]
                            ),
                        }
                    )
                case "thoughts":
                    chatlog.append(
                        {
                            "role": "user",
                            "content": messageTemplates["thought_for_events"](
                                event["timestamp"], event["value"]["content"]
                            ),
                        }
                    )
                case "messages":
                    if event["value"]["role"] == "user":
                        chatlog.append(
                            {
                                "role": "user",
                                "content": messageTemplates[
                                    "message_received_for_events"
                                ](
                                    event["timestamp"],
                                    event["value"]["content"],
                                    self.username,
                                ),
                            }
                        )
                    else:
                        chatlog.append(
                            {
                                "role": "user",
                                "content": messageTemplates["message_user_for_events"](
                                    event["timestamp"],
                                    event["value"]["content"],
                                    self.username,
                                ),
                            }
                        )
        chatlog.append(
            {
                "role": "user",
                "content": messageTemplates["describe_event_now"](
                    convert_dt_ts(datetime.now(timezone.utc))
                ),
            }
        )
        return chatlog


def _convert_messages_to_chatlog(messages: List[Message]) -> List[Dict[str, str]]:
    chat: List[Dict[str, str]] = []
    for message in messages:
        chat.append(
            {
                "role": message["role"],
                "content": message["content"],
            }
        )
    return chat


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
