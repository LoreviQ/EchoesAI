"""Database types."""

from typing import Callable

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    func,
)

metadata_obj = MetaData()
func: Callable

character_table = Table(
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

event_table = Table(
    "events",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("timestamp", DateTime, default=func.now()),
    Column("char_id", ForeignKey("characters.id"), nullable=False),
    Column("type", String, nullable=False),
    Column("content", String, nullable=False),
)

posts_table = Table(
    "posts",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("timestamp", DateTime, default=func.now()),
    Column("char_id", ForeignKey("characters.id"), nullable=False),
    Column("content", String),
    Column("image_post", Boolean, default=False),
    Column("image_description", String, default=""),
    Column("prompt", String, default=""),
    Column("image_path", String, default=""),
)

users_table = Table(
    "users",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("username", String, nullable=False),
    Column("password", String, nullable=False),
    Column("email", String, nullable=False),
)

threads_table = Table(
    "threads",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("started", DateTime, default=func.now()),
    Column("user_id", ForeignKey("users.id"), nullable=False),
    Column("char_id", ForeignKey("characters.id"), nullable=False),
)

messages_table = Table(
    "messages",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("timestamp", DateTime, default=func.now()),
    Column("thread_id", ForeignKey("threads.id"), nullable=False),
    Column("content", String, nullable=False),
    Column("role", String, nullable=False),
)
