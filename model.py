"""
Module for Hugging face pipeline for text generation.
"""

import os
import time
from typing import Dict, List, Protocol, Tuple

import torch
from transformers import AutoTokenizer, Pipeline, pipeline


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
        self.tokenizer = AutoTokenizer.from_pretrained("Sao10K/L3-8B-Stheno-v3.2")

    def generate_response(
        self, chat: List[Dict[str, str]], max_new_tokens: int = 512
    ) -> Dict[str, str]:
        """
        Generate a new message based on the chat history.
        """
        return self.model.generate_response(chat, max_new_tokens)

    def token_count(self, chat: List[Dict[str, str]]) -> int:
        """
        Return the number of tokens of a chat.
        """
        return sum(len(self.tokenizer.encode(m["content"])) for m in chat)


class ModelActual(ModelInterface):
    """
    Class to manage the Hugging Face pipeline for text generation.
    """

    def __init__(self) -> None:
        self.pipe, self.max_tokens = self._load_model()

    def _load_model(self) -> Tuple[Pipeline, int]:
        """
        Load the model.
        """
        # prep torch
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = (
            "garbage_collection_threshold:0.9,max_split_size_mb:128 "
            "python launch.py --precision full --no-half --opt-sub-quad-attention"
        )
        torch.cuda.empty_cache()
        pipe = pipeline(
            "text-generation",
            model="Sao10K/L3-8B-Stheno-v3.2",
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        max_tokens = pipe.model.config.max_position_embeddings
        return pipe, max_tokens

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
        self.pipe, self.max_tokens = self._load_model()

    def _load_model(self) -> Tuple[None, int]:
        """
        Load the model.
        """
        return None, 8192

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
