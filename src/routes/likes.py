""" Routes for likes."""

from typing import List

from flask import Response, jsonify, make_response, request

import database as db

from .main import bp
from .posts import _convert_character_to_posted_by
from .route_types import Comment


@bp.route("/v1/user/<int:user_id>/likes", methods=["POST"])
def post_like(
    user_id: int,
) -> Response:
    """Posts a like."""
    data = request.get_json()
    if not all(key in data for key in ("content_type", "content_id")):
        return make_response("missing required fields", 400)
    content_type = data["content_type"]
    content_id = int(data["content_id"])
    if content_type == "post":
        db.insert_like(
            db.Like(
                user_id=user_id,
                content_liked=content_type,
                post_id=content_id,
            )
        )
    elif content_type == "comment":
        db.insert_like(
            db.Like(
                user_id=user_id,
                content_liked=content_type,
                comment_id=content_id,
            )
        )
    return make_response("", 200)


# delete like
@bp.route("/v1/user/<int:user_id>/likes", methods=["DELETE"])
def delete_like(
    user_id: int,
) -> Response:
    """Deletes a like."""
    data = request.get_json()
    if not all(key in data for key in ("content_type", "content_id")):
        return make_response("missing required fields", 400)
    content_type = data["content_type"]
    content_id = int(data["content_id"])
    like = db.select_likes(
        db.Like(
            user_id=user_id,
            content_liked=content_type,
            content_id=content_id,
        )
    )
    db.delete_like(like["id"][0])
    return make_response("", 200)
