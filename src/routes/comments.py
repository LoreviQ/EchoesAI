"""
Routes for posts.
Some comments are included in post responses.
"""

from typing import List

from flask import Response, jsonify, make_response

import database as db

from .main import bp
from .posts import _convert_character_to_posted_by
from .route_types import Comment


@bp.route("/v1/posts/<int:post_id>/comments", methods=["GET"])
def get_comments_by_post(post_id: int) -> Response:
    """Gets all comments for a post."""
    try:
        db.select_post(post_id)
    except ValueError:
        return make_response("post not found", 404)
    comments = db.select_comments(db.Comment(post_id=post_id))
    response: List[Comment] = []
    for comment in comments:
        character = db.select_character_by_id(comment["char_id"])
        response.append(
            {
                "id": comment["id"],
                "timestamp": comment["timestamp"],
                "content": comment["content"],
                "posted_by": _convert_character_to_posted_by(character),
            }
        )
    return make_response(jsonify(response), 200)
