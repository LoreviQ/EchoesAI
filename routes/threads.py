"""Routes for threads."""

import urllib.parse

from flask import Response, jsonify, make_response, request

import database as db

from .main import bp


@bp.route("/threads/new", methods=["POST"])
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
        character = db.select_character_by_path(character_path)
    except ValueError:
        return make_response("character not found", 400)
    thread_id = db.insert_thread(user["id"], character["id"])
    return make_response(str(thread_id), 200)


@bp.route("/threads/<string:username>", methods=["GET"])
def get_threads_by_user(username: str) -> Response:
    """Gets all threads for a user."""
    decoded_username = urllib.parse.unquote(username)
    try:
        db.select_user(decoded_username)
    except ValueError:
        return make_response("user not found", 400)
    threads = db.select_threads_by_user(decoded_username)
    return make_response(jsonify(threads), 200)
