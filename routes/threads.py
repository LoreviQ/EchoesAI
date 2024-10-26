"""Routes for threads."""

from flask import Response, jsonify, make_response, request

import database as db

from .main import bp


@bp.route("/threads/new", methods=["POST"])
def new_thread() -> Response:
    """Creates a new thread."""
    data = request.get_json()
    username = data["username"]
    character = data["character"]
    thread_id = db.insert_thread(username, character)
    return make_response(str(thread_id), 200)


@bp.route("/threads/<string:username>", methods=["GET"])
def get_threads_by_user(username: str) -> Response:
    """Gets all threads for a user."""
    threads = db.select_threads_by_user(username)
    return make_response(jsonify(threads), 200)
