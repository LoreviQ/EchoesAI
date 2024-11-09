"""Types for routes to return specific data."""

from datetime import datetime
from typing import List, TypedDict


class PostedBy(TypedDict):
    """Reduced data for the character who posted a comment."""

    id: int
    name: str
    path_name: str
    profile_path: str
    favorite_colour: str


class Comment(TypedDict):
    """Reduced data for a comment."""

    id: int
    timestamp: datetime
    content: str
    posted_by: PostedBy


class PostWithComments(TypedDict):
    """All the data required to render a post with comments."""

    id: int
    timestamp: datetime
    posted_by: PostedBy
    content: str
    image_post: bool
    image_description: str
    prompt: str
    comments_count: int
    comments: List[Comment]
