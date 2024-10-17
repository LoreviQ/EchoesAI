"""
Module to manage the chatbot state.
"""

import json
from typing import Dict, List, Optional

from jinja2 import Template

from database import DB
from model import MockedModel, Model


class Chatbot:
    """
    Class to manage a chatbot state.
    """

    def __init__(
        self,
        username: str,
        character: str,
        thread_id: int,
        database: Optional[DB] = None,
    ) -> None:
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

    def new_model(self, mocked: bool = False) -> None:
        """
        Create a new model instance.
        """
        if mocked:
            self.model = MockedModel()
        else:
            self.model = Model()

    def set_thread(self, thread_id: int) -> List[Dict[str, str]]:
        """
        Set the chat thread from the database.
        """
        if not self.database:
            print(
                "No database provided. Starting new chat. WARNING: Chat will not be saved."
            )
            return [
                {
                    "role": "assistant",
                    "content": self.character_info["initial_message"],
                }
            ]
        messages = self.database.get_messages_by_thread(thread_id)
        if len(messages) == 0:
            print("No messages found in the database. Starting new chat.")
            return [
                {
                    "role": "assistant",
                    "content": self.character_info["initial_message"],
                }
            ]
        chat_log: List[Dict[str, str]] = []
        for message in messages:
            chat_log.append(
                {
                    "role": message[4],
                    "content": message[3],
                }
            )
        return chat_log

    def get_system_message(self, system_message_type: str) -> Dict[str, str]:
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

        return {
            "role": "system",
            "content": current_content,
        }

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
            [self.primary_system_message] + self.primary_chat, max_new_tokens=512
        )
