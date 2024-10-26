"""Routes for threads."""

from flask import Response, make_response, request

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
