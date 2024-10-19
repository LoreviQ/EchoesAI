"""
Module for Hugging face pipeline for text generation.
"""

import os
import time
from typing import Dict, List, Protocol

import torch
from transformers import Pipeline, pipeline


class ModelInterface(Protocol):
    """
    Interface for the model class.
    """

    def generate_response(
        self, chat: List[Dict[str, str]], max_new_tokens: int = 512
    ) -> Dict[str, str]:
        """
        Generate a new message based on the chat history.
        """


class Model:
    """
    Class to manage the model instance.
    """

    def __init__(self, model: ModelInterface) -> None:
        self.model = model

    def generate_response(
        self, chat: List[Dict[str, str]], max_new_tokens: int = 512
    ) -> Dict[str, str]:
        """
        Generate a new message based on the chat history.
        """
        return self.model.generate_response(chat, max_new_tokens)


class ModelActual(ModelInterface):
    """
    Class to manage the Hugging Face pipeline for text generation.
    """

    def __init__(self) -> None:
        self.pipe = self._load_model()

    def _load_model(self) -> Pipeline:
        """
        Load the model.
        """
        # prep torch
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = (
            "garbage_collection_threshold:0.9,max_split_size_mb:128 "
            "python launch.py --precision full --no-half --opt-sub-quad-attention"
        )
        torch.cuda.empty_cache()
        return pipeline(
            "text-generation",
            model="Sao10K/L3-8B-Stheno-v3.2",
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )

    def generate_response(
        self, chat: List[Dict[str, str]], max_new_tokens: int = 512
    ) -> Dict[str, str]:
        """
        Generate a new message based on the chat history.
        """
        if chat[-1]["role"] == "assistant":
            raise ValueError("Most recent message in chat is from assistant.")
        response = self.pipe(chat, max_new_tokens=max_new_tokens)
        return response[0]["generated_text"][-1]


class ModelMocked(ModelInterface):
    """
    Mock class for testing
    """

    def __init__(self, time_to_respond: str) -> None:
        self.time_to_respond = time_to_respond

    def generate_response(
        self, chat: List[Dict[str, str]], max_new_tokens: int = 512
    ) -> Dict[str, str]:
        """
        Mocked generate_response method.
        """
        time.sleep(1)
        # time checker behavior
        if "You need to respond with the time" in chat[0]["content"]:
            if self.time_to_respond == "short":
                return {"content": "30s", "role": "assistant"}
            return {"content": "5m", "role": "assistant"}

        # chat message behavior
        return {"content": "Mock response", "role": "assistant"}
