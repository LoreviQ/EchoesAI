"""Database types."""

from datetime import datetime
from typing import TypedDict

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    func,
)
from typing_extensions import NotRequired

metadata_obj = MetaData()


class Character(TypedDict, total=False):
    """Character type."""

    id: NotRequired[int]
    name: NotRequired[str]
    path_name: NotRequired[str]
    description: NotRequired[str]
    age: NotRequired[int]
    height: NotRequired[str]
    personality: NotRequired[str]
    appearance: NotRequired[str]
    loves: NotRequired[str]
    hates: NotRequired[str]
    details: NotRequired[str]
    scenario: NotRequired[str]
    important: NotRequired[str]
    initial_message: NotRequired[str]
    favorite_colour: NotRequired[str]
    phases: NotRequired[bool]
    img_gen: NotRequired[bool]
    model: NotRequired[str]
    global_positive: NotRequired[str]
    global_negative: NotRequired[str]
    profile_path: NotRequired[str]


characters_table = Table(
    "characters",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("path_name", String, nullable=False),
    Column("description", String),
    Column("age", Integer),
    Column("height", String),
    Column("personality", String),
    Column("appearance", String),
    Column("loves", String),
    Column("hates", String),
    Column("details", String),
    Column("scenario", String),
    Column("important", String),
    Column("initial_message", String),
    Column("favorite_colour", String),
    Column("phases", Boolean, default=False),
    Column("img_gen", Boolean, default=False),
    Column("model", String),
    Column("global_positive", String),
    Column("global_negative", String),
    Column("profile_path", String),
)


class Event(TypedDict, total=False):
    """Event type."""

    id: NotRequired[int]
    timestamp: NotRequired[datetime]
    char_id: NotRequired[int]
    type: NotRequired[str]
    content: NotRequired[str]


events_table = Table(
    "events",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("timestamp", DateTime, default=func.now()),  # pylint: disable=not-callable
    Column("char_id", ForeignKey("characters.id"), nullable=False),
    Column("type", String, nullable=False),
    Column("content", String, nullable=False),
)


class Post(TypedDict, total=False):
    """Post type."""

    id: NotRequired[int]
    timestamp: NotRequired[datetime]
    char_id: NotRequired[int]
    content: NotRequired[str]
    image_post: NotRequired[bool]
    image_description: NotRequired[str]
    prompt: NotRequired[str]
    image_path: NotRequired[str]


posts_table = Table(
    "posts",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("timestamp", DateTime, default=func.now()),  # pylint: disable=not-callable
    Column("char_id", ForeignKey("characters.id"), nullable=False),
    Column("content", String),
    Column("image_post", Boolean, default=False),
    Column("image_description", String, default=""),
    Column("prompt", String, default=""),
    Column("image_path", String, default=""),
)


class Comment(TypedDict, total=False):
    """Comments type."""

    id: NotRequired[int]
    timestamp: NotRequired[datetime]
    post_id: NotRequired[int]
    char_id: NotRequired[int]
    content: NotRequired[str]


comments_table = Table(
    "comments",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("timestamp", DateTime, default=func.now()),  # pylint: disable=not-callable
    Column("post_id", ForeignKey("posts.id"), nullable=False),
    Column("char_id", ForeignKey("characters.id"), nullable=False),
    Column("content", String, nullable=False),
)


class User(TypedDict, total=False):
    """User type."""

    id: NotRequired[int]
    username: NotRequired[str]
    password: NotRequired[str]
    email: NotRequired[str]


users_table = Table(
    "users",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("username", String, nullable=False),
    Column("password", String, nullable=False),
    Column("email", String, nullable=False),
)


class Thread(TypedDict, total=False):
    """Thread type."""

    id: NotRequired[int]
    started: NotRequired[datetime]
    user_id: NotRequired[int]
    char_id: NotRequired[int]


threads_table = Table(
    "threads",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("started", DateTime, default=func.now()),  # pylint: disable=not-callable
    Column("user_id", ForeignKey("users.id"), nullable=False),
    Column("char_id", ForeignKey("characters.id"), nullable=False),
)


class Message(TypedDict, total=False):
    """Message type."""

    id: NotRequired[int]
    timestamp: NotRequired[datetime]
    thread_id: NotRequired[int]
    content: NotRequired[str]
    role: NotRequired[str]


messages_table = Table(
    "messages",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("timestamp", DateTime, default=func.now()),  # pylint: disable=not-callable
    Column("thread_id", ForeignKey("threads.id"), nullable=False),
    Column("content", String, nullable=False),
    Column("role", String, nullable=False),
)


class Like(TypedDict, total=False):
    """Type for likes"""

    id: NotRequired[int]
    timestamp: NotRequired[datetime]
    user_id: NotRequired[int]
    content_liked: NotRequired[str]  # currently supports posts and comments
    post_id: NotRequired[int]
    comment_id: NotRequired[int]


likes_table = Table(
    "likes",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("timestamp", DateTime, default=func.now()),  # pylint: disable=not-callable
    Column("user_id", ForeignKey("users.id"), nullable=False),
    Column("content_liked", String, nullable=False),
    Column("post_id", ForeignKey("posts.id"), nullable=True),
    Column("comment_id", ForeignKey("comments.id"), nullable=True),
    CheckConstraint(
        "(post_id IS NOT NULL AND comment_id IS NULL) OR "
        "(post_id IS NULL AND comment_id IS NOT NULL)",
        name="check_one_type_not_null",
    ),
)


class QueryOptions(TypedDict, total=False):
    """Type for query options"""

    limit: NotRequired[int]
    offset: NotRequired[int]
    orderby: NotRequired[str]
    order: NotRequired[str]
