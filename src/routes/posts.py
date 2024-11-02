"""Routes for posts."""

from flask import Response, jsonify, make_response, request

import database as db

from .main import bp


@bp.route("/v1/posts", methods=["GET"])
def get_posts() -> Response:
    """Gets all posts, optionally with a query."""
    query_params = request.args.to_dict()
    try:
        post_query = _create_post_query_params(query_params)
    except ValueError:
        return make_response(jsonify([]), 200)
    posts = db.select_posts(post_query)
    return make_response(jsonify(posts), 200)


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
