"""Routes for users."""

from flask import Response, jsonify, make_response, request

import auth
import database as db

from .main import _create_query_params, bp
from .threads import _create_thread_params


@bp.route("/v1/users", methods=["POST"])
def post_user() -> Response:
    """Creates a new user."""
    data = request.get_json()
    if not all(key in data for key in ("username", "password", "email")):
        return make_response("", 400)
    user = db.User(
        username=data["username"],
        password=data["password"],
        email=data["email"],
    )
    assert user["username"]
    auth.insert_user(user)
    token = auth.issue_access_token(user["username"])
    return make_response(token, 200)


@bp.route("/v1/login", methods=["POST"])
def login() -> Response:
    """Logs in a user."""
    data = request.get_json()
    if not all(key in data for key in ("username", "password")):
        return make_response("", 400)
    username = data["username"]
    password = data["password"]
    if not auth.authenticate_user(username, password):
        return make_response("", 401)

    token = auth.issue_access_token(username)
    return make_response(token, 200)


@bp.route("/v1/users/<string:username>/threads", methods=["GET"])
def get_threads_by_user(username: str) -> Response:
    """Gets all threads for a user."""
    # build query
    try:
        user = db.select_user(username)
    except ValueError:
        return make_response("user not found", 400)
    assert user["id"]
    query_params = request.args.to_dict()
    thread_query = _create_thread_params(query_params)
    thread_query["user_id"] = user["id"]
    options = _create_query_params(query_params)
    threads = db.select_threads(thread_query, options)
    response = []
    for thread in threads:
        character = db.select_character_by_id(thread["char_id"])
        response.append(
            {
                "id": thread["id"],
                "started": thread["started"],
                "character": character["name"],
                "char_path": character["path_name"],
                "profile_path": character["profile_path"],
                "recent_message": "",
            }
        )
    return make_response(jsonify(response), 200)
