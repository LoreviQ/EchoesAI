"""Routes for characters."""

from flask import Response, jsonify, make_response, request

import database as db

from .main import bp


@bp.route("/v1/characters", methods=["POST"])
def post_character() -> Response:
    """Creates a new character."""
    data = request.get_json()
    if not all(key in data for key in ("name", "path_name")):
        return make_response("Missing required fields", 400)
    character = _create_character_query_params(data)
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
    try:
        character_query = _create_character_query_params(query_params)
    except ValueError:
        return make_response(jsonify([]), 200)
    characters = db.select_characters(character_query)
    return make_response(jsonify(characters), 200)


@bp.route("/v1/characters/<string:char_path>/posts", methods=["GET"])
def get_posts_by_character(char_path: str) -> Response:
    """Gets all posts for a character."""
    try:
        character = db.select_character(char_path)
    except ValueError:
        return make_response("character not found", 404)
    posts = db.select_posts(db.Post(char_id=character["id"]))
    return make_response(jsonify(posts), 200)


@bp.route("/v1/characters/<string:char_path>/events", methods=["GET"])
def get_events_by_character(char_path: str) -> Response:
    """Gets all events for a character."""
    try:
        character = db.select_character(char_path)
    except ValueError:
        return make_response("character not found", 404)
    events = db.select_events(db.Event(char_id=character["id"]))
    return make_response(jsonify(events), 200)


def _create_character_query_params(query_params: dict[str, str]) -> db.Character:
    character_query = db.Character()
    # basic params
    if "id" in query_params and query_params["id"]:
        character_query["id"] = int(query_params["id"])
    if "name" in query_params and query_params["name"]:
        character_query["name"] = query_params["name"]
    if "path_name" in query_params and query_params["path_name"]:
        character_query["path_name"] = query_params["path_name"]
    if "description" in query_params and query_params["description"]:
        character_query["description"] = query_params["description"]
    if "age" in query_params and query_params["age"]:
        character_query["age"] = int(query_params["age"])
    if "height" in query_params and query_params["height"]:
        character_query["height"] = query_params["height"]
    if "personality" in query_params and query_params["personality"]:
        character_query["personality"] = query_params["personality"]
    if "appearance" in query_params and query_params["appearance"]:
        character_query["appearance"] = query_params["appearance"]
    if "loves" in query_params and query_params["loves"]:
        character_query["loves"] = query_params["loves"]
    if "hates" in query_params and query_params["hates"]:
        character_query["hates"] = query_params["hates"]
    if "details" in query_params and query_params["details"]:
        character_query["details"] = query_params["details"]
    if "scenario" in query_params and query_params["scenario"]:
        character_query["scenario"] = query_params["scenario"]
    if "important" in query_params and query_params["important"]:
        character_query["important"] = query_params["important"]
    if "initial_message" in query_params and query_params["initial_message"]:
        character_query["initial_message"] = query_params["initial_message"]
    if "favorite_colour" in query_params and query_params["favorite_colour"]:
        character_query["favorite_colour"] = query_params["favorite_colour"]
    if "phases" in query_params and query_params["phases"]:
        character_query["phases"] = bool(query_params["phases"])
    if "img_gen" in query_params and query_params["img_gen"]:
        character_query["img_gen"] = bool(query_params["img_gen"])
    if "model" in query_params and query_params["model"]:
        character_query["model"] = query_params["model"]
    if "global_positive" in query_params and query_params["global_positive"]:
        character_query["global_positive"] = query_params["global_positive"]
    if "global_negative" in query_params and query_params["global_negative"]:
        character_query["global_negative"] = query_params["global_negative"]
    if "profile_path" in query_params and query_params["profile_path"]:
        character_query["profile_path"] = query_params["profile_path"]
    return character_query
