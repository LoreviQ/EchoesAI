"""
Module experimenting with the Hugging Face pipeline for text generation 
to create a chatbot.
"""

import json
import os

import torch
from transformers import pipeline


class Chatbot:
    """
    Class to manage a chatbot generated though the Hugging Face pipeline.
    """

    def __init__(self, character):
        # Load character information
        with open(f"characters/{character}.json", "r", encoding="utf-8") as file:
            self.character_info = json.load(file)

        # prep torch
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = (
            "garbage_collection_threshold:0.9,max_split_size_mb:512 "
            "python launch.py --precision full --no-half --opt-sub-quad-attention"
        )
        torch.cuda.empty_cache()

        # Load the model
        self.pipe = pipeline(
            "text-generation",
            model="Sao10K/L3-8B-Stheno-v3.2",
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )

        # Initialize chat
        self.chat = []
        self.time = []
        self.phase = 0
        self.set_system_message(self.chat, "chat_message")
        self.chat.append(
            {
                "role": "assistant",
                "content": f"{self.character_info['initial_message']}",
            }
        )

    def set_system_message(self, chat, system_message_type):
        """
        Change the system message between several preconfigured options.
        """
        initial_section = ""
        match system_message_type:
            case "chat_message":
                initial_section = f"""
You are an expert actor who can fully immerse yourself in any role. You do not break character for any reason, even if someone tries addressing you as an AI or language model.
Currently, your role is {self.character_info['char']}, which is described in detail below. As {self.character_info['char']}, continue the exchange with the user.
"""
            case "time_checker":
                initial_section = f"""
You are playing the role of {self.character_info['char']}, which is described in detail below. 
You are currently in a conversation with the user. You need to respond with the time it will take to respond to the user's message.
The current response requency of {self.character_info['char']} is dictated by: {self.character_info['phases'][self.phase]['response']} 
Reply with a duration in the format of number followed by a time unit (e.g., 12h for 12 hours, 15s for 15 seconds, or 2h 20m for 2 hours and 20 minutes).
Do not add any additional information to your response.
"""

        system_message = {
            "role": "system",
            "content": f"""
{initial_section}
Description: {self.character_info['description']}
Age: {self.character_info['age']}
Personality: {self.character_info['personality']}
Appearance: {self.character_info['appearance']}
Loves: {self.character_info['loves']}
Hates: {self.character_info['hates']}
Details: {self.character_info['details']}

The story follows the scenario: {self.character_info['scenario']}
The story progresses in phases. 
The currently active phase is: {self.character_info['phases'][self.phase]['name']} 
Described by: {self.character_info['phases'][self.phase]['description']}
{self.character_info['char']} uses the following names for the user: {self.character_info['phases'][self.phase]['names']} 

The following is highly important to remember: {self.character_info['important']}
""",
        }
        if chat:
            chat[0] = system_message
        else:
            chat.append(system_message)

    def add_message(self, message):
        """
        Add a message to the chat log.
        """
        message_role = message["role"]
        if self.chat[-1]["role"] == message_role:
            raise ValueError(
                f"Most recent message in chat already from {message_role}."
            )
        self.chat.append(message)

    def get_response(self, max_new_tokens=512):
        """
        Get a response from the chatbot.
        """
        if self.chat[-1]["role"] == "assistant":
            raise ValueError("Most recent message in chat is from assistant.")
        response = self.pipe(self.chat, max_new_tokens=max_new_tokens)
        return response[0]["generated_text"][-1]

    def check_time(self, new_check_chain=False, new_message=None):
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
        response = self.pipe(self.time, max_new_tokens=16)
        self.time.append(response[0]["generated_text"][-1])
        print("Time taken to respond:", response[0]["generated_text"][-1])

    def _new_check_time(self):
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

    def _continue_check_time(self, new_message):
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
