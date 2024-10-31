"""Routes for posts."""

from flask import Response, jsonify, make_response, request

import database_old as db

from .main import bp


@bp.route("/v1/posts", methods=["GET"])
def get_posts() -> Response:
    """Gets all posts, optionally with a query."""
    query_params = request.args.to_dict()
    post_query = db.Event(**query_params)
    if "char_path" in query_params:
        chars = db.select_characters(db.Character(path_name=query_params["char_path"]))
        if not chars:
            return make_response(jsonify([]), 200)
        post_query["char_id"] = chars[0]["id"]
        del post_query["char_path"]

    posts = db.select_posts(post_query)
    return make_response(jsonify(posts), 200)
