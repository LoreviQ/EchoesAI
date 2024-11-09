from typing import Any, List

from sqlalchemy import insert, select

from .db_types import Like, likes_table
from .main import ENGINE


def _row_to_like(row: dict[str, Any]) -> Like:
    """Convert a row to a like."""
    return Like(
        id=row.id,
        timestamp=row.timestamp,
        user_id=row.user_id,
        content_liked=row.content_liked,
        post_id=row.post_id,
        comment_id=row.comment_id,
    )


def insert_like(values: Like) -> int:
    """Insert a like into the database."""
    stmt = insert(likes_table).values(values)
    with ENGINE.begin() as conn:
        result = conn.execute(stmt)
        return result.inserted_primary_key[0]


def select_likes(like_query: Like = Like()) -> List[Like]:
    """Select likes from the database."""
    conditions = []
    for key, value in like_query.items():
        conditions.append(getattr(likes_table.c, key) == value)
    stmt = select(likes_table).where(*conditions)
    with ENGINE.connect() as conn:
        result = conn.execute(stmt)
        return [_row_to_like(row) for row in result]


def count_likes(content_type: str, content_id: int) -> int:
    """Count the number of likes for a given content type and id."""
    stmt = (
        likes_table.count()
        .where(likes_table.c.content_liked == content_type)
        .where(likes_table.c.content_id == content_id)
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
        .where(likes_table.c.content_id == content_id)
    )
    with ENGINE.connect() as conn:
        result = conn.execute(stmt)
        return result.scalar() > 0


def delete_like(like_id: int) -> None:
    """Delete a like from the database."""
    stmt = likes_table.delete().where(likes_table.c.id == like_id)
    with ENGINE.begin() as conn:
        conn.execute(stmt)
