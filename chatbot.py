"""
Module to manage the chatbot state.
"""

import json
from typing import Dict, List, Optional

from jinja2 import Template

from model import MockedModel, Model


class Chatbot:
    """
    Class to manage a chatbot state.
    """

    def __init__(self, username: str, character: str, mocked: bool = False) -> None:
        self.username = username
        # Load character information
        with open(f"characters/{character}.json", "r", encoding="utf-8") as file:
            self.character_info = json.load(file)
        # Load the model
        if mocked:
            self.model = MockedModel()
        else:
            self.model = Model()
        # Initialize chat
        self.chat: List[Dict[str, str]] = []
        self.time: List[Dict[str, str]] = []
        self.phase = 0
        self.set_system_message(self.chat, "chat_message")
        self.chat.append(
            {
                "role": "assistant",
                "content": f"{self.character_info['initial_message']}",
            }
        )

    def set_system_message(
        self, chat: List[Dict[str, str]], system_message_type: str
    ) -> None:
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

        system_message = {
            "role": "system",
            "content": current_content,
        }
        if chat:
            chat[0] = system_message
        else:
            chat.append(system_message)

    def add_message(self, message: Dict[str, str]) -> None:
        """
        Add a message to the chat log.
        """
        message_role = message["role"]
        if self.chat[-1]["role"] == message_role:
            raise ValueError(
                f"Most recent message in chat already from {message_role}."
            )
        self.chat.append(message)

    def get_response(self) -> Dict[str, str]:
        """
        Generate a response from the chatbot.
        """
        return self.model.generate_response(self.chat, max_new_tokens=512)

    def check_time(
        self,
        new_check_chain: bool = False,
        new_message: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Check how long the chatbot will take to respond to a message.
        """
        # Override new_check_chain if self.time is empty
        if not self.time:
            new_check_chain = True
        if new_check_chain:
            self._new_check_time()
        else:
            self._continue_check_time(new_message)
        response = self.model.generate_response(self.time, max_new_tokens=32)
        return response["content"]

    def _new_check_time(self) -> None:
        if self.chat[-1]["role"] == "assistant":
            raise ValueError("Most recent message in chat is from assistant.")
        self.time = self.chat.copy()
        self.set_system_message(self.time, "time_checker")
        self.time[-1] = {
            "role": "user",
            "content": f"""
{{user}} is sending you the following message:
{self.time[-1]["content"]}
How long will you take to respond to it? Reply with a duration in the format of number followed by a time unit 
(e.g., 12h for 12 hours, 15s for 15 seconds, or 2h 20m for 2 hours and 20 minutes).
""",
        }

    def _continue_check_time(self, new_message: Optional[Dict[str, str]]) -> None:
        if not new_message:
            raise ValueError("No new message provided.")
        self.time.append(
            {
                "role": "user",
                "content": f"""
{{user}} is sending you another message:
{new_message["content"]}
Does this change the time you will take to respond to it? Reply with a duration in the format of number followed by a time unit
(e.g., 12h for 12 hours, 15s for 15 seconds, or 2h 20m for 2 hours and 20 minutes).
""",
            }
        )
