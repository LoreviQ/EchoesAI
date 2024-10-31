"""Database operations for the posts table."""

from typing import Any, List

from sqlalchemy import insert, select
from sqlalchemy.engine import Row

from .db_types import Post, posts_table
from .main import ENGINE


def _row_to_post(row: Row[Any]) -> Post:
    """Convert a row to a post."""
    return Post(
        id=row.id,
        timestamp=row.timestamp,
        char_id=row.char_id,
        content=row.content,
        image_post=row.image_post,
        image_description=row.image_description,
        prompt=row.prompt,
        image_path=row.image_path,
    )


def insert_post(values: Post) -> int:
    """Insert a post into the database."""
    stmt = insert(posts_table).values(values)
    with ENGINE.begin() as conn:
        result = conn.execute(stmt)
        return result.inserted_primary_key[0]


def select_post(post_id: int) -> Post:
    """Select a post from the database."""
    stmt = select(posts_table).where(posts_table.c.id == post_id)
    with ENGINE.connect() as conn:
        result = conn.execute(stmt)
        post = result.fetchone()
        if post is None:
            raise ValueError(f"no post found with id: {post_id}")
        return _row_to_post(post)


def update_post_with_image_path(post_id: int, image_path: str) -> None:
    """Add an image path to a post."""
    stmt = (
        posts_table.update()
        .where(posts_table.c.id == post_id)
        .values(image_path=image_path)
    )
    with ENGINE.begin() as conn:
        conn.execute(stmt)


def select_posts(post_query: Post = Post()) -> List[Post]:
    """Select posts from the database, optionally with a query."""
    conditions = []
    for key, value in post_query.items():
        conditions.append(getattr(posts_table.c, key) == value)
    stmt = select(posts_table).where(*conditions)
    with ENGINE.connect() as conn:
        result = conn.execute(stmt)
        return [_row_to_post(row) for row in result]
