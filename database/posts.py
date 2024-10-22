from datetime import datetime
from typing import List, TypedDict

from .main import (
    connect_to_db,
    convert_ts_dt,
    general_commit_returning_none,
    general_insert_returning_id,
)


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


def insert_social_media_post(post: Post) -> int:
    """
    Insert a post into the database.
    """
    query = """
        INSERT INTO posts (character, description, prompt, caption) 
        VALUES (?, ?, ?, ?) 
        RETURNING id
    """
    return general_insert_returning_id(
        query,
        (
            post["character"],
            post["description"],
            post["prompt"],
            post["caption"],
        ),
    )


def add_image_path_to_post(post_id: int, image_path: str) -> None:
    """
    Add an image path to a post.
    """
    query = """
        UPDATE posts 
        SET image_path = ? 
        WHERE id = ?
    """
    general_commit_returning_none(query, (image_path, post_id))


def get_posts_by_character(character: int) -> List[Post]:
    """
    Get all posts from the database.
    """
    query = """
        SELECT id, timestamp, description, prompt, caption, image_path
        FROM posts 
        WHERE character = ?
    """

    _, cursor, close = connect_to_db()
    cursor.execute(
        query,
        (character,),
    )
    result = cursor.fetchall()
    close()
    posts: List[Post] = []
    for post in result:
        posts.append(
            Post(
                id=post[0],
                timestamp=convert_ts_dt(post[1]),
                character=character,
                description=post[2],
                prompt=post[3],
                caption=post[4],
                image_path=post[5],
            )
        )
    return posts
