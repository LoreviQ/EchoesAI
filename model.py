"""
Module for Hugging face pipeline for text generation.
"""

import os
from typing import Dict

import torch
from transformers import pipeline


class Model:
    """
    Class to manage the Hugging Face pipeline for text generation.
    """

    def __init__(self):
        # prep torch
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = (
            "garbage_collection_threshold:0.9,max_split_size_mb:128 "
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

    def generate_response(self, chat, max_new_tokens: int = 512) -> Dict[str, str]:
        """
        Generate a new message based on the chat history.
        """
        if chat[-1]["role"] == "assistant":
            raise ValueError("Most recent message in chat is from assistant.")
        response = self.pipe(chat, max_new_tokens=max_new_tokens)
        return response[0]["generated_text"][-1]
