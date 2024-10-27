"""Type definitions and variable decarations for chatbot package."""

from datetime import datetime
from typing import TypedDict

MAX_TOKENS = 4096
MAX_NEW_TOKENS = 512


class ChatMessage(TypedDict):
    """Chat message type."""

    role: str
    content: str


class StampedChatMessage(TypedDict):
    """Chat message type."""

    role: str
    content: str
    timestamp: datetime


class ImageGenerationFailedException(Exception):
    """Exception raised when image generation fails on Civitai's side."""
