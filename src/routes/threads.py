"""Routes for threads."""

from flask import Response, jsonify, make_response, request

import database as db

from .main import _create_query_params, bp


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
        character = db.select_character(character_path)
    except ValueError:
        return make_response("invalid payload", 400)
    assert user["id"]
    assert character["id"]
    thread_id = db.insert_thread(db.Thread(user_id=user["id"], char_id=character["id"]))
    return make_response(str(thread_id), 200)


@bp.route("/v1/threads", methods=["GET"])
def get_threads() -> Response:
    """Get threads, optionally with a query."""
    query_params = request.args.to_dict()
    thread_query = db.Thread()
    try:
        thread_query = _create_thread_params(query_params)
        options = _create_query_params(query_params)
    except ValueError:
        return make_response(jsonify([]), 200)
    threads = db.select_threads(thread_query, options)
    return make_response(jsonify(threads), 200)


def _create_thread_params(query_params: dict[str, str]) -> db.Thread:
    thread_query = db.Thread()
    # basic params
    if "id" in query_params:
        thread_query["id"] = int(query_params["id"])
    if "user_id" in query_params:
        thread_query["user_id"] = int(query_params["user_id"])
    if "char_id" in query_params:
        thread_query["char_id"] = int(query_params["char_id"])
    # custom params
    if "char_path" in query_params:
        character = db.select_character(query_params["char_path"])
        thread_query["char_id"] = character["id"]
    if "username" in query_params:
        user = db.select_user(query_params["username"])
        thread_query["user_id"] = user["id"]
    return thread_query
