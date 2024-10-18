"""
Module to manage the chatbot state.
"""

import json
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

    def generate_new_message(self) -> bool:
        """
        Handles the entire response cycle for recieving and generating a new message.
        """
        # get a response from the model
        system_message = self.get_system_message("chat_message")
        response = self.get_response(system_message, self.chatlog)
        self.database.post_message(self.thread, response["content"], response["role"])
