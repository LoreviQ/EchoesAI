"""Database operations for the posts table."""

from typing import List

from .main import (
    _placeholder_gen,
    connect_to_db,
    general_commit_returning_none,
    general_insert_returning_id,
)
from .types import Post


def insert_social_media_post(post: Post) -> int:
    """
    Insert a post into the database.
    """
    ph = _placeholder_gen()
    query = f"""
        INSERT INTO posts (char_id, description, image_post, prompt, caption) 
        VALUES ({next(ph)}, {next(ph)}, {next(ph)}, {next(ph)}, {next(ph)}) 
        RETURNING id
    """
    return general_insert_returning_id(
        query,
        (
            post["char_id"],
            post["description"],
            post["image_post"],
            post["prompt"],
            post["caption"],
        ),
    )


def update_post_with_image_path(post_id: int, image_path: str) -> None:
    """
    Add an image path to a post.
    """
    ph = _placeholder_gen()
    query = f"""
        UPDATE posts 
        SET image_path = {next(ph)} 
        WHERE id = {next(ph)}
    """
    general_commit_returning_none(query, (image_path, post_id))


def select_posts(post_query: Post = Post()) -> List[Post]:
    """
    Get all posts from the database based on a query.
    """
    ph = _placeholder_gen()
    query = """
        SELECT id, timestamp, char_id, description, image_post, prompt, caption, image_path
        FROM posts 
    """
    conditions = []
    parameters = []
    for key, value in post_query.items():
        if value is not None:
            conditions.append(f"{key} = {next(ph)}")
            parameters.append(value)
    if conditions:
        query += " WHERE "
        query += " AND ".join(conditions)

    _, cursor, close = connect_to_db()
    cursor.execute(query, parameters)
    results = cursor.fetchall()
    close()

    posts: List[Post] = []
    for post in results:
        posts.append(
            Post(
                id=post[0],
                timestamp=post[1],
                char_id=post[2],
                description=post[3],
                image_post=post[4],
                prompt=post[5],
                caption=post[6],
                image_path=post[7],
            )
        )
    return posts