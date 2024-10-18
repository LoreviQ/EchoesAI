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
    ) -> None:
        username, character = database.get_thread(thread_id)
        self.username = username
        # Load character information
        with open(f"characters/{character}.json", "r", encoding="utf-8") as file:
            self.character_info = json.load(file)

        self.model: Model | MockedModel
        self.database = database

        # Initialize chat
        self.phase = 0
        self.primary_system_message = self.get_system_message("chat_message")
        self.primary_chat = self.set_thread(thread_id)

    def set_thread(self, thread_id: int) -> List[Dict[str, str]]:
        """
        Set the chat thread from the database.
        """
        # if new, start a new chat
        default_return: List[Dict[str, str]] = []
        if self.character_info["initial_message"]:
            default_return.append(
                {
                    "role": "assistant",
                    "content": self.character_info["initial_message"],
                }
            )
        if not self.database:
            print("No database provided. WARNING: Chat will not be saved.")
            return default_return
        messages = self.database.get_messages_by_thread(thread_id)
        if len(messages) == 0:
            print("No messages found in the database. Starting new chat.")
            return default_return

        # return chat log from database
        chat_log: List[Dict[str, str]] = []
        for message in messages:
            chat_log.append(
                {
                    "role": message[2],
                    "content": message[1],
                }
            )
        return chat_log

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

    def add_message(self, message: Dict[str, str]) -> None:
        """
        Add a message to the chat log.
        """
        message_role = message["role"]
        if self.primary_chat[-1]["role"] == message_role:
            raise ValueError(
                f"Most recent message in chat already from {message_role}."
            )
        self.primary_chat.append(message)

    def get_response(self) -> Dict[str, str]:
        """
        Generate a response from the chatbot.
        """
        return self.model.generate_response(
            self.primary_system_message + self.primary_chat, max_new_tokens=512
        )
