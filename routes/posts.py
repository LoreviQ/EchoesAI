"""Routes for posts."""

from typing import Dict, List

from flask import Response, jsonify, make_response

import database as db

from .main import bp


@bp.route("/posts/<string:char_path>", methods=["GET"])
def get_posts_by_character(char_path: str) -> Response:
    """Gets all posts for a character."""
    character = db.select_character_by_path(char_path)
    assert character["id"]
    posts = db.posts.get_posts_by_character(character["id"])
    response: List[Dict[str, str]] = []
    for post in posts:
        response.append(
            {
                "id": post["id"],
                "timestamp": db.convert_dt_ts(post["timestamp"]),
                "description": post["description"],
                "image_post": post["image_post"],
                "prompt": post["prompt"],
                "caption": post["caption"],
                "image_path": post["image_path"],
            },
        )
    return make_response(jsonify(response), 200)
