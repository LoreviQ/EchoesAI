"""
Module to manage the chatbot state.
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List

from jinja2 import Template

from database import DB
from model import MockedModel, Model


class Chatbot:
    """
    Class to manage a chatbot state.
    """

    def __init__(
        self,
        thread_id: int,
        database: DB,
        model: Model | MockedModel,
    ) -> None:
        self.thread = thread_id
        self.database = database
        self.model = model

        username, character, phase = database.get_thread(thread_id)
        self.username = username
        self.phase = phase
        with open(f"characters/{character}.json", "r", encoding="utf-8") as file:
            self.character_info = json.load(file)

        self.chatlog = self._initialise_chatlog()

    def _initialise_chatlog(self) -> List[Dict[str, str]]:
        """
        Initialise the chatlog from the database.
        """
        messages = self.database.get_messages_by_thread(self.thread)
        return [
            {"role": message[2], "content": message[1], "timestamp": message[3]}
            for message in messages
        ]

    def get_system_message(self, system_message_type: str) -> List[Dict[str, str]]:
        """
        Change the system message between several preconfigured options.
        """
        match system_message_type:
            case "chat_message":
                template_filename = "main.txt"
            case "time_checker":
                template_filename = "time.txt"
            case _:
                raise ValueError(f"Invalid system message type: {system_message_type}")

        with open(f"templates/{template_filename}", "r", encoding="utf-8") as file:
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

    def get_response(
        self, system_message: List[Dict[str, str]], chat: List[Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Generate a response from the chatbot.
        """
        return self.model.generate_response(system_message + chat, max_new_tokens=512)

    def response_cycle(self) -> None:
        """
        Handles the entire response cycle for recieving and generating a new message.
        """
        # get response time
        system_message_time = self.get_system_message("time_checker")
        chat = self.chatlog
        chat[-1][
            "content"
        ] = f"""
        User has sent you the following message:
        {chat[-1]["content"]}
        How long will it take you to respond?
        """
        response = self.get_response(system_message_time, chat)
        duration = _parse_time(response["content"])

        # get a response from the model
        system_message_chat = self.get_system_message("chat_message")
        response = self.get_response(system_message_chat, self.chatlog)
        timestamp = None
        if duration > timedelta(minutes=1):
            timestamp = datetime.now() + duration
        self.database.post_message(
            self.thread, response["content"], response["role"], timestamp
        )


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
