"""Routes for characters."""

from flask import Response, jsonify, make_response, request

import database as db

from .main import bp


@bp.route("/v1/characters", methods=["POST"])
def new_character() -> Response:
    """Creates a new character."""
    data = request.get_json()
    if not all(key in data for key in ("name", "path_name")):
        return make_response("Missing required fields", 400)
    character = db.Character(
        name=data["name"],
        path_name=data["path_name"],
        description=data.get("description", ""),
        age=data.get("age", 0),
        height=data.get("height", 0),
        personality=data.get("personality", ""),
        appearance=data.get("appearance", ""),
        loves=data.get("loves", ""),
        hates=data.get("hates", ""),
        details=data.get("details", ""),
        scenario=data.get("scenario", ""),
        important=data.get("important", ""),
        initial_message=data.get("initial_message", ""),
        favorite_colour=data.get("favorite_colour", ""),
        phases=data.get("phases", False),
        img_gen=data.get("img_gen", False),
        model=data.get("model", ""),
        global_positive=data.get("global_positive", ""),
        global_negative=data.get("global_negative", ""),
        profile_path=data.get("profile_path", ""),
    )
    db.insert_character(character)
    return make_response(str(data["path_name"]), 200)


@bp.route("/v1/characters/<string:char_path>", methods=["GET"])
def get_character(char_path: str) -> Response:
    """Gets a character by path name."""
    try:
        character = db.select_character(char_path)
        return make_response(jsonify(character), 200)
    except ValueError:
        return make_response("character not found", 404)


@bp.route("/v1/characters", methods=["GET"])
def get_characters() -> Response:
    """Get characters, optionally with a query."""
    query_params = request.args.to_dict()
    character_query = db.Character(**query_params)
    characters = db.select_characters(character_query)
    return make_response(jsonify(characters), 200)


@bp.route("/v1/characters/<string:char_path>/posts", methods=["GET"])
def get_posts_by_character(char_path: str) -> Response:
    """Gets all posts for a character."""
    try:
        character = db.select_character(char_path)
    except ValueError:
        return make_response("character not found", 404)
    posts = db.select_posts(db.Post(character=character["id"]))
    return make_response(jsonify(posts), 200)


@bp.route("/v1/characters/<string:char_path>/events", methods=["GET"])
def get_events_by_character(char_path: str) -> Response:
    """Gets all events for a character."""
    try:
        character = db.select_character(char_path)
    except ValueError:
        return make_response("character not found", 404)
    events = db.select_events(db.Event(character=character["id"]))
    return make_response(jsonify(events), 200)
