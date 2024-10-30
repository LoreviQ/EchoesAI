"""Routes for threads."""

from flask import Response, jsonify, make_response, request

import database as db

from .main import bp


@bp.route("/v1/threads", methods=["POST"])
def new_thread() -> Response:
    """Creates a new thread."""
    data = request.get_json()
    if not all(key in data for key in ("username", "character")):
        return make_response("missing required fields", 400)
    username = data["username"]
    character_path = data["character"]
    try:
        user = db.select_user(username)
    except ValueError:
        return make_response("user not found", 400)
    try:
        character = db.select_characters(db.Character(path_name=character_path))[0]
    except IndexError:
        return make_response("character not found", 400)
    assert user["id"]
    assert character["id"]
    thread_id = db.insert_thread(user["id"], character["id"])
    return make_response(str(thread_id), 200)


@bp.route("/v1/threads", methods=["GET"])
def get_threads() -> Response:
    """Get threads, optionally with a query."""
    query_params = request.args.to_dict()
    # build query
    thread_query = db.Thread(
        id=query_params.get("id"),
        user_id=query_params.get("user_id"),
        char_id=query_params.get("char_id"),
        phase=query_params.get("phase"),
    )
    if "char_path" in query_params:
        chars = db.select_characters(db.Character(path_name=query_params["char_path"]))
        if not chars:
            return make_response(jsonify([]), 200)
        thread_query["char_id"] = chars[0]["id"]
    if "username" in query_params:
        try:
            user = db.select_user(query_params["username"])
        except ValueError:
            return make_response(jsonify([]), 200)
        thread_query["user_id"] = user["id"]
    options = db.QueryOptions(
        limit=query_params.get("limit"),
        orderby=query_params.get("orderby"),
        order=query_params.get("order"),
    )
    threads = db.select_threads(thread_query, options)
    return make_response(jsonify(threads), 200)
