"""Routes for posts."""

from typing import List

from flask import Response, jsonify, make_response, request

import database as db

from .main import _create_query_params, bp
from .route_types import PostedBy, PostWithComments


@bp.route("/v1/posts", methods=["GET"])
def get_posts() -> Response:
    """Gets all posts, optionally with a query."""
    query_params = request.args.to_dict()
    try:
        post_query = _create_post_query_params(query_params)
        options = _create_query_params(query_params)
    except ValueError:
        return make_response(jsonify([]), 200)
    posts = db.select_posts(post_query, options)
    response = _convert_posts_to_post_with_comments(posts)
    return make_response(jsonify(response), 200)


def _create_post_query_params(query_params: dict[str, str]) -> db.Post:
    post_query = db.Post()
    # basic params
    if "id" in query_params:
        post_query["id"] = int(query_params["id"])
    if "char_id" in query_params:
        post_query["char_id"] = int(query_params["char_id"])
    if "content" in query_params:
        post_query["content"] = query_params["content"]
    if "image_post" in query_params:
        post_query["image_post"] = bool(query_params["image_post"])
    if "image_description" in query_params:
        post_query["image_description"] = query_params["image_description"]
    if "prompt" in query_params:
        post_query["prompt"] = query_params["prompt"]
    if "image_path" in query_params:
        post_query["image_path"] = query_params["image_path"]
    # custom params
    if "char_path" in query_params:
        character = db.select_character(query_params["char_path"])
        post_query["char_id"] = character["id"]
    return post_query


def _convert_posts_to_post_with_comments(
    posts: List[db.Post],
) -> List[PostWithComments]:
    """Converts a list of posts to a list of posts with comments."""
    posts_w_comments: PostWithComments = []
    for post in posts:
        character = db.select_character_by_id(post["char_id"])
        post_with_comments = {
            "id": post["id"],
            "timestamp": post["timestamp"],
            "posted_by": _convert_character_to_posted_by(character),
            "content": post["content"],
            "image_post": post["image_post"],
            "image_path": post["image_path"],
            "image_description": post["image_description"],
            "prompt": post["prompt"],
        }
        post_with_comments["comments"] = []
        comments = db.select_comments(db.Comment(post_id=post["id"]))
        for comment in comments:
            character = db.select_character_by_id(comment["char_id"])
            comment_to_appened = {
                "id": comment["id"],
                "timestamp": comment["timestamp"],
                "content": comment["content"],
                "posted_by": _convert_character_to_posted_by(character),
            }
            post_with_comments["comments"].append(comment_to_appened)
        posts_w_comments.append(post_with_comments)
    return posts_w_comments


def _convert_character_to_posted_by(
    character: db.Character,
) -> PostedBy:
    """Converts a character to a posted by response."""
    return PostedBy(
        id=character["id"],
        name=character["name"],
        path_name=character["path_name"],
        profile_path=character["profile_path"],
        favorite_colour=character["favorite_colour"],
    )
