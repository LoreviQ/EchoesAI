"""
Module to manage the chatbot state.
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List

from jinja2 import Template

from database import DB
from model import Model

messageTemplates = {
    "time_to_respond": lambda user, message: f"{user} has sent you the following message:\n{message}\nHow long will it take you to respond?",
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

        self.chatlog = self._initialise_chatlog()

    def _initialise_chatlog(self) -> List[Dict[str, any]]:
        """
        Initialise the chatlog from the database.
        """
        messages = self.database.get_messages_by_thread(self.thread)
        return [
            {
                "role": message[2],
                "content": message[1],
                "timestamp": datetime.strptime(message[3], "%Y-%m-%d %H:%M:%S"),
            }
            for message in messages
        ]

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
        chat = self.chatlog
        chat[-1]["content"] = messageTemplates["time_to_respond"](
            self.username, chat[-1]["content"]
        )
        response = self._generate_text(sys_message, chat)
        return _parse_time(response["content"])

    def response_cycle(self, duration: timedelta | None = None) -> None:
        """
        Handles the entire response cycle for recieving and generating a new message.
        """
        # get response time
        if duration is None:
            duration = self._get_response_time()
        timestamp = datetime.now() + duration
        # get a response from the model
        sys_message = self.get_system_message("chat")
        response = self._generate_text(sys_message, self.chatlog)
        self.database.post_message(
            self.thread, response["content"], response["role"], timestamp
        )

    def generate_event(self, event_type: str) -> None:
        """
        Generate an event message.
        """
        sys_message = self.get_system_message(event_type)
        events = self.database.get_events_by_type_and_chatbot("event", self.character)
        thoughts = self.database.get_events_by_type_and_chatbot(
            "thought", self.character
        )
        messages = self.chatlog
        all_events = self._combine_events(
            ("events", events), ("thoughts", thoughts), ("messages", messages)
        )
        custom_chatlog = self._event_chatlog(all_events)
        response = self._generate_text(sys_message, custom_chatlog)
        self.database.post_event(self.character, event_type, response["content"])

    def _combine_events(self, *event_lists) -> List[Dict[str, any]]:
        result = []
        for event_list in event_lists:
            for event in event_list:
                result.append(
                    {
                        "type": event_list[0],
                        "timestamp": event["timestamp"],
                        "value": event,
                    }
                )
        return sorted(result, key=lambda x: x["timestamp"])

    def _event_chatlog(self, events: List[Dict[str, any]]) -> List[Dict[str, str]]:
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
                    datetime.now().strftime("%H:%M:%S")
                ),
            }
        )
        return chatlog


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
