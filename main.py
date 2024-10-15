import json
import os

import torch
from transformers import pipeline


class Chatbot:
    def __init__(self, character):
        # Load character information
        with open(f"details/{character}.json", "r", encoding="utf-8") as file:
            self.character_info = json.load(file)

        # prep torch
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = (
            "garbage_collection_threshold:0.9,max_split_size_mb:512 python launch.py --precision full --no-half --opt-sub-quad-attention"
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
        self.phase = "INTRODUCTION_PHASE"
        self.set_system_message("INTRODUCTION_PHASE")
        self.chat.append(
            {
                "role": "assistant",
                "content": f"{self.character_info['initial_message']}",
            }
        )

    def set_system_message(self, system_message_type):
        initial_section = ""
        match system_message_type:
            case "chat_message":
                initial_section = f"""
You are an expert actor that can fully immerse yourself into any role given. You do not break character for any reason, even if someone tries addressing you as an AI or language model.
Currently your role is {self.character_info['char']}, which is described in detail below. As {self.character_info['char']}, continue the exchange with the user.
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
The story progresses in phases. The currently active phase is {self.phase} described by: {self.character_info['phases'][self.phase]}

The following is highly important to remember: {self.character_info['important']}
""",
        }
        if self.chat:
            self.chat[0] = system_message
        else:
            self.chat.append(system_message)

    def get_response(self, next_message, max_new_tokens=512):
        self.chat.append(next_message)
        response = self.pipe(self.chat, max_new_tokens=max_new_tokens)
        self.chat = response[0]["generated_text"]

    def check_time(self, next_message, max_new_tokens=32):
        message = {
            "role": "user",
            "content": f"""
{{user}} is sending you the message:
{next_message["content"]}
How long will you take to respond to it? Reply with a duration in the format of number followed by a time unit (e.g., 12h for 12 hours, 15s for 15 seconds, or 2h 20m for 2 hours and 20 minutes).
""",
        }
        temp_chat = self.chat.copy()
        temp_chat.append(message)
        response = self.pipe(temp_chat, max_new_tokens=max_new_tokens)
        print("Time taken to respond:", response[0]["generated_text"][-1]["content"])

    def handle_input(self, user_input):
        match user_input.lower():
            case "exit" | "quit":
                print("Ending the session. Goodbye!")
                return False
            case _:
                next_message = {
                    "role": "user",
                    "content": user_input,
                }
                self.check_time(next_message)
                self.get_response(next_message)
                print(self.chat[-1]["content"])
                return True

    def start_chat(self):
        print("Bot params:")
        print(self.chat[-2]["content"])
        print("Starting conversation:")
        print(self.chat[-1]["content"])
        while True:
            user_input = input("")
            if not self.handle_input(user_input):
                break


if __name__ == "__main__":
    char_name = "ophelia"
    chatbot = Chatbot(char_name)
    chatbot.start_chat()
