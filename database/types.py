from datetime import datetime
from typing import TypedDict


class Character(TypedDict):
    """
    Character type.
    """

    id: int
    name: str
    description: str
    age: int
    height: str
    personality: str
    appearance: str
    loves: str
    hates: str
    details: str
    scenario: str
    important: str
    initial_message: str
    favorite_colour: str
    phases: bool
    img_gen: bool
    model: str
    global_positive: str
    global_negative: str
    additional_networks: str  # string representation of json


class Thread(TypedDict):
    """
    Thread type.
    """

    id: int
    started: datetime
    user: str
    character: int
    phase: int


class Message(TypedDict):
    """
    Message type.
    """

    id: int
    timestamp: datetime
    thread: Thread
    content: str
    role: str


class Event(TypedDict):
    """
    Event type.
    """

    id: int
    timestamp: datetime
    character: int
    type: str
    content: str


class Post(TypedDict):
    """
    Post type.
    """

    id: int
    timestamp: datetime
    character: int
    description: str
    prompt: str
    caption: str
    image_path: str
