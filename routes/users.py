"""Routes for users."""

from flask import Response, make_response, request

import auth
import database as db

from .main import bp


@bp.route("/users/new", methods=["POST"])
def new_user() -> Response:
    """Creates a new user."""
    data = request.get_json()
    if not all(key in data for key in ("username", "password", "email")):
        return make_response("", 400)
    user = db.User(
        username=data["username"],
        password=data["password"],
        email=data["email"],
    )
    auth.insert_user(user)
    token = auth.issue_access_token(user["username"])
    return make_response(token, 200)


@bp.route("/login", methods=["POST"])
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
