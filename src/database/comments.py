"""Database operations for the comments table."""

from typing import Any, List

from sqlalchemy import insert, select
from sqlalchemy.engine import Row

from .db_types import Comment, Post, comments_table
from .main import ENGINE


def _row_to_comment(row: Row[Any]) -> Comment:
    """Convert a row to a comment."""
    return Comment(
        id=row.id,
        timestamp=row.timestamp,
        post_id=row.post_id,
        char_id=row.char_id,
        content=row.content,
    )


def insert_comment(values: Comment) -> int:
    """Insert a comment into the database."""
    stmt = insert(comments_table).values(values)
    with ENGINE.begin() as conn:
        result = conn.execute(stmt)
        return result.inserted_primary_key[0]


def select_comments(comment_query: Comment = Comment()) -> List[Comment]:
    """Select comments from the database, optionally with a query."""
    conditions = []
    for key, value in comment_query.items():
        conditions.append(getattr(comments_table.c, key) == value)
    stmt = select(comments_table).where(*conditions)
    with ENGINE.connect() as conn:
        result = conn.execute(stmt)
        return [_row_to_comment(row) for row in result]


def select_comments_from_post(post_id: int) -> List[Comment]:
    """Select comments related to a post."""
    stmt = select(comments_table).where(comments_table.c.post_id == post_id)
    with ENGINE.connect() as conn:
        result = conn.execute(stmt)
        return [_row_to_comment(row) for row in result]
