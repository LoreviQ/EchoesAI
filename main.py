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
        self.set_system_message("INTRODUCTION_PHASE")
        self.chat.append(
            {
                "role": "assistant",
                "content": f"{self.character_info['initial_message']}",
            }
        )

    def set_system_message(self, phase):
        system_message = {
            "role": "system",
            "content": f"""
You are an expert actor that can fully immerse yourself into any role given. You do not break character for any reason, even if someone tries addressing you as an AI or language model.

Currently your role is {self.character_info['char']}, which is described in detail below. As {self.character_info['char']}, continue the exchange with the user.
Description: {self.character_info['description']}
Age: {self.character_info['age']}
Personality: {self.character_info['personality']}
Appearance: {self.character_info['appearance']}
Loves: {self.character_info['loves']}
Hates: {self.character_info['hates']}
Details: {self.character_info['details']}

The story follows the scenario: {self.character_info['scenario']}
The story progresses in phases. The currently active phase is {phase} described by: {self.character_info['phases'][phase]}
""",
        }
        if self.chat:
            self.chat[0] = system_message
        else:
            self.chat.append(system_message)

    def add_user_input(self, user_input):
        self.chat.append({"role": "user", "content": user_input})

    def add_response(self, max_new_tokens=512):
        response = self.pipe(self.chat, max_new_tokens=max_new_tokens)
        self.chat.append(
            {
                "role": "assistant",
                "content": response[0]["generated_text"][-1]["content"],
            }
        )

    def handle_input(self, user_input):
        match user_input.lower():
            case "exit" | "quit":
                print("Ending the session. Goodbye!")
                return False
            case _:
                self.add_user_input(user_input)
                self.add_response()
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
