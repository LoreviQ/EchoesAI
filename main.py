import json
import os

import torch
from transformers import pipeline

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = (
    "garbage_collection_threshold:0.9,max_split_size_mb:512 python launch.py --precision full --no-half --opt-sub-quad-attention"
)
torch.cuda.empty_cache()


# Load character information from JSON file
with open("details/ophelia.json", "r", encoding="utf-8") as file:
    character_info = json.load(file)

# Initialize the pipeline
pipe = pipeline(
    "text-generation",
    model="Sao10K/L3-8B-Stheno-v3.2",
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Update the chat list with character information
chat = [
    {
        "role": "system",
        "content": f"""
You are an expert actor that can fully immerse yourself into any role given. You do not break character for any reason, even if someone tries addressing you as an AI or language model.

Currently your role is {character_info['char']}, which is described in detail below. As {character_info['char']}, continue the exchange with the user.
Description: {character_info['description']}
Age: {character_info['age']}
Personality: {character_info['personality']}
Appearance: {character_info['appearance']}
Loves: {character_info['loves']}
Hates: {character_info['hates']}
Details: {character_info['details']}

The story follows the scenario: {character_info['scenario']}
The story progresses in phases. The currently active phase is: {character_info['phases']["INTRODUCTION PHASE"]}
""",
    },
    {
        "role": "assistant",
        "content": """
Hey. I'm lonely, want to chat?
""",
    },
]

print("Bot params:")
print(chat[-2]["content"])
print("Starting conversation:")
print(chat[-1]["content"])
while True:
    user_input = input("")
    message = {"role": "user", "content": user_input}
    chat.append(message)
    response = pipe(chat, max_new_tokens=128)
    chat.append({"role": "assistant", "content": response[0]["generated_text"]})
    print(chat[-1]["content"])
