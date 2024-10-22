"""
Module for Hugging face pipeline for text generation.
"""

import os
import time
from typing import Dict, List, Protocol, Tuple

import torch
from transformers import AutoTokenizer, Pipeline, pipeline

MODEL = "meta-llama/Llama-3.2-3B-Instruct"


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
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL)
        self.mocked = isinstance(model, ModelMocked)

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
            "garbage_collection_threshold:0.8,max_split_size_mb:128 "
            "python launch.py --opt-sub-quad-attention"
        )
        torch.cuda.empty_cache()
        torch.cuda.set_per_process_memory_fraction(0.95, device=0)
        pipe = pipeline(
            "text-generation",
            model=MODEL,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        max_tokens = pipe.model.config.max_position_embeddings
        return pipe, max_tokens

    def generate_response(
        self, chat: List[Dict[str, str]], max_new_tokens: int = 256
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

        # event behavior
        if "short description of what you're currently doing" in chat[0]["content"]:
            return {"content": "Mock event", "role": "assistant"}

        # thought behavior
        if "what you're currently thinking" in chat[0]["content"]:
            return {"content": "Mock thought", "role": "assistant"}

        # photo behavior
        if "Describe in detail the photo you post." in chat[0]["content"]:
            return {"content": MOCK_IMAGE_DESCRIPTION, "role": "assistant"}

        # SD behavior
        if "stable diffusion text2image prompt" in chat[0]["content"]:
            return {"content": MOCK_SD_PROMPT, "role": "assistant"}

        # Caption behavior
        if "a caption for your post" in chat[0]["content"]:
            return {"content": MOCK_CAPTION, "role": "assistant"}

        # chat message behavior
        return {"content": "Mock response", "role": "assistant"}


MOCK_IMAGE_DESCRIPTION = """It's 5:30 PM, and Ophelia has just wrapped up a long day of content creation. The lighting in the room is golden and soft, with sunlight streaming in from a large window behind her, casting a warm glow across the space. The photo is a medium shot, taken from a slightly high camera angle, which gives it a casual, "caught in the moment" feel. Ophelia is the only subject in the frame.

She's lounging comfortably on a plush velvet couch, legs stretched out in front of her, slightly crossed at the ankles. Her left arm is resting on the armrest of the couch, while her right hand is holding up a half-empty glass of iced coffee, tilted toward the camera as if she's about to take a sip. She's looking directly at the camera with a playful smirk, one eyebrow slightly raised as if she's sharing an inside joke with her followers.

Ophelia is dressed in a cozy yet stylish outfit: an oversized, pastel pink hoodie that falls just past her hips and a pair of black biker shorts. She’s barefoot, with one foot playfully dangling off the edge of the couch. She's wearing minimal jewelry—just a simple silver necklace and small hoop earrings. Her makeup is natural, with dewy skin, a touch of blush, and glossy lips. Her raven-black hair is pulled back into a high, slightly messy ponytail, with a few loose strands framing her face, adding to the laid-back vibe.

In the background, there’s a glimpse of her workspace—an open laptop, a half-eaten snack, and a few skincare products scattered on a table—giving the scene an authentic, relatable touch that her audience loves."""

MOCK_SD_PROMPT = "Ophelia, single subject, female, medium shot, high angle, lounging on velvet couch, legs stretched, crossed ankles, left arm on armrest, right hand holding iced coffee, looking at camera, playful smirk, golden hour lighting, sunlight through window, oversized pink hoodie, black biker shorts, barefoot, silver necklace, small hoop earrings, minimal makeup, dewy skin, high ponytail, loose strands, casual room, workspace in background, laptop, snack, skincare products."

MOCK_CAPTION = "Is it still ‘work’ if I’m lounging in a hoodie with iced coffee? Asking for a friend… 😏 #ContentCreatorLife #ComfyButMakeItCute #GoldenHourVibes"
