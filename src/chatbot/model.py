"""Module for Hugging face pipeline for text generation."""

import os
import time
from typing import List, Protocol, Tuple

import torch
from transformers import AutoTokenizer, Pipeline, pipeline

from .types import ChatMessage


class ModelInterface(Protocol):
    """
    Interface for the model class.
    """

    def generate_response(
        self, chat: List[ChatMessage], max_new_tokens: int = 512
    ) -> ChatMessage:
        """
        Generate a new message based on the chat history.
        """


class Model:
    """
    Class to manage the model instance.
    """

    def __init__(self, model: ModelInterface) -> None:
        self.model = model
        self.tokenizer = AutoTokenizer.from_pretrained(self.model.model_name)
        self.mocked = isinstance(model, ModelMocked)

    def generate_response(
        self, chat: List[ChatMessage], max_new_tokens: int = 512
    ) -> ChatMessage:
        """
        Generate a new message based on the chat history.
        """
        return self.model.generate_response(chat, max_new_tokens)

    def token_count(self, chat: List[ChatMessage]) -> int:
        """
        Return the number of tokens of a chat.
        """
        return sum(len(self.tokenizer.encode(m["content"])) for m in chat)


class ModelActual(ModelInterface):
    """
    Class to manage the Hugging Face pipeline for text generation.
    """

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.pipe, self.max_tokens = self._load_model()

    def _load_model(self) -> Tuple[Pipeline, int]:
        """
        Load the model.
        """
        # prep torch
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = (
            "garbage_collection_threshold:0.8,max_split_size_mb:128 "
            "python launch.py --opt-sub-quad-attention"
        )
        torch.cuda.empty_cache()
        torch.cuda.set_per_process_memory_fraction(0.95, device=0)
        pipe = pipeline(
            "text-generation",
            model=self.model_name,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        max_tokens = pipe.model.config.max_position_embeddings
        return pipe, max_tokens

    def generate_response(
        self, chat: List[ChatMessage], max_new_tokens: int = 256
    ) -> ChatMessage:
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

    def __init__(self, model_name: str, time_to_respond: str) -> None:
        self.model_name = model_name
        self.time_to_respond = time_to_respond
        self.pipe, self.max_tokens = self._load_model()

    def _load_model(self) -> Tuple[None, int]:
        """
        Load the model.
        """
        return None, 8192

    def generate_response(
        self, chat: List[ChatMessage], max_new_tokens: int = 512
    ) -> ChatMessage:
        """
        Mocked generate_response method.
        """
        time.sleep(1)
        # time checker behavior
        if "You need to respond with the time" in chat[0]["content"]:
            if self.time_to_respond == "short":
                return {"content": "1s", "role": "assistant"}
            return {"content": "10s", "role": "assistant"}

        # event behavior
        if "short description of what you're currently doing" in chat[0]["content"]:
            return {"content": "Mock event", "role": "assistant"}

        # thought behavior
        if "what you're currently thinking" in chat[0]["content"]:
            return {"content": "Mock thought", "role": "assistant"}

        # photo behavior
        if "Describe in detail the photo you post." in chat[0]["content"]:
            return {"content": "Mock Image Description", "role": "assistant"}

        # SD behavior
        if "stable diffusion text2image prompt" in chat[0]["content"]:
            return {"content": "Mock SD prompt", "role": "assistant"}

        # Caption behavior
        if "a caption for your post" in chat[0]["content"]:
            return {"content": "Mock Caption", "role": "assistant"}

        # chat message behavior
        return {"content": "Mock response", "role": "assistant"}


def new_model(
    model_name: str = "meta-llama/Llama-3.2-3B-Instruct", mocked: bool = False
) -> Model:
    """Create a new model instance."""
    if mocked:
        return Model(ModelMocked(model_name, "short"))
    return Model(ModelActual(model_name))
