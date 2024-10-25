"""Database types."""

from datetime import datetime
from typing import Optional, TypedDict


class Character(TypedDict, total=False):
    """Character type."""

    id: Optional[int]
    name: Optional[str]
    path_name: Optional[str]
    description: Optional[str]
    age: Optional[int]
    height: Optional[str]
    personality: Optional[str]
    appearance: Optional[str]
    loves: Optional[str]
    hates: Optional[str]
    details: Optional[str]
    scenario: Optional[str]
    important: Optional[str]
    initial_message: Optional[str]
    favorite_colour: Optional[str]
    phases: Optional[bool]
    img_gen: Optional[bool]
    model: Optional[str]
    global_positive: Optional[str]
    global_negative: Optional[str]
    profile_path: Optional[str]


class Thread(TypedDict, total=False):
    """Thread type."""

    id: Optional[int]
    started: Optional[datetime]
    user: Optional[str]
    character: Optional[int]
    phase: Optional[int]


class Message(TypedDict, total=False):
    """Message type."""

    id: Optional[int]
    timestamp: Optional[datetime]
    thread: Optional[Thread]
    content: Optional[str]
    role: Optional[str]


class Event(TypedDict, total=False):
    """Event type."""

    id: Optional[int]
    timestamp: Optional[datetime]
    character: Optional[int]
    type: Optional[str]
    content: Optional[str]


class Post(TypedDict, total=False):
    """Post type."""

    id: Optional[int]
    timestamp: Optional[datetime]
    character: Optional[int]
    description: Optional[str]
    image_post: Optional[bool]
    prompt: Optional[str]
    caption: Optional[str]
    image_path: Optional[str]


class User(TypedDict, total=False):
    """User type."""

    id: Optional[int]
    username: Optional[str]
    password: Optional[str]
    email: Optional[str]
