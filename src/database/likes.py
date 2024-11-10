"""Database operations for the likes table."""

from typing import Any, List

from sqlalchemy import func, insert, select

from .db_types import Like, likes_table
from .main import ENGINE


def _row_to_like(row: dict[str, Any]) -> Like:
    """Convert a row to a like."""
    content_id: int
    if row.post_id:
        content_id = row.post_id
    elif row.comment_id:
        content_id = row.comment_id
    return Like(
        id=row.id,
        timestamp=row.timestamp,
        user_id=row.user_id,
        content_liked=row.content_liked,
        content_id=content_id,
    )


def _like_to_values(like: Like) -> dict[str, Any]:
    """Convert a like to a dictionary of values."""
    values = like.copy()
    content_liked = like.get("content_liked")
    if content_liked:
        if content_liked == "post":
            values["post_id"] = like["content_id"]
        elif content_liked == "comment":
            values["comment_id"] = like["content_id"]
        del values["content_id"]
    return values


def insert_like(like: Like) -> int:
    """Insert a like into the database."""
    values = _like_to_values(like)
    stmt = insert(likes_table).values(values)
    with ENGINE.begin() as conn:
        result = conn.execute(stmt)
        return result.inserted_primary_key[0]


def select_likes(like_query: Like = Like()) -> List[Like]:
    """Select likes from the database."""
    conditions = []
    values_query = _like_to_values(like_query)
    for key, value in values_query.items():
        conditions.append(getattr(likes_table.c, key) == value)
    stmt = select(likes_table).where(*conditions)
    with ENGINE.connect() as conn:
        result = conn.execute(stmt)
        return [_row_to_like(row) for row in result]


def count_likes(content_type: str, content_id: int) -> int:
    """Count the number of likes for a given content type and id."""
    stmt = (
        select(func.count())  # pylint: disable=not-callable
        .where(likes_table.c.content_liked == content_type)
        .where(getattr(likes_table.c, content_type + "_id") == content_id)
    )
    with ENGINE.connect() as conn:
        result = conn.execute(stmt)
        return result.scalar()


def has_user_liked(user_id: int, content_type: str, content_id: int) -> bool:
    """Check if a user has liked a given content type and id."""
    stmt = (
        likes_table.select()
        .where(likes_table.c.user_id == user_id)
        .where(likes_table.c.content_liked == content_type)
        .where(getattr(likes_table.c, content_type + "_id") == content_id)
    )
    with ENGINE.connect() as conn:
        result = conn.execute(stmt)
        if result.scalar():
            return True
        return False


def delete_like(like_id: int) -> None:
    """Delete a like from the database."""
    stmt = likes_table.delete().where(likes_table.c.id == like_id)
    with ENGINE.begin() as conn:
        conn.execute(stmt)
