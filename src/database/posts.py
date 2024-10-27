"""Database operations for the posts table."""

from typing import List

from .main import (
    connect_to_db,
    general_commit_returning_none,
    general_insert_returning_id,
)
from .types import Post


def insert_social_media_post(post: Post) -> int:
    """
    Insert a post into the database.
    """
    query = """
        INSERT INTO posts (character, description, image_post, prompt, caption) 
        VALUES (?, ?, ?, ?, ?) 
        RETURNING id
    """
    return general_insert_returning_id(
        query,
        (
            post["character"],
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
    query = """
        UPDATE posts 
        SET image_path = ? 
        WHERE id = ?
    """
    general_commit_returning_none(query, (image_path, post_id))


def select_posts(post_query: Post = Post()) -> List[Post]:
    """
    Get all posts from the database based on a query.
    """
    query = """
        SELECT id, timestamp, character, description, image_post, prompt, caption, image_path
        FROM posts 
    """
    conditions = []
    parameters = []
    for key, value in post_query.items():
        if value is not None:
            conditions.append(f"{key} = ?")
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
                character=post[2],
                description=post[3],
                image_post=post[4],
                prompt=post[5],
                caption=post[6],
                image_path=post[7],
            )
        )
    return posts
