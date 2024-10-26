"""Routes for characters."""

from flask import Response, jsonify, make_response, request

import database as db

from .main import bp


@bp.route("/characters/new", methods=["POST"])
def new_character() -> Response:
    """Creates a new character."""
    data = request.get_json()
    character = db.Character(
        name=data["name"],
        path_name=data["path_name"],
        description=data["description"],
        age=data["age"],
        height=data["height"],
        personality=data["personality"],
        appearance=data["appearance"],
        loves=data["loves"],
        hates=data["hates"],
        details=data["details"],
        scenario=data["scenario"],
        important=data["important"],
        initial_message=data["initial_message"],
        favorite_colour=data["favorite_colour"],
        phases=False,
        img_gen=data["img_gen"],
        model=data["model"],
        global_positive=data["global_positive"],
        global_negative=data["global_negative"],
    )
    db.insert_character(character)
    return make_response(str(data["path_name"]), 200)


@bp.route("/characters/id/<int:character_id>", methods=["GET"])
def get_character(character_id: int) -> Response:
    """Gets a character by ID."""
    character = db.select_character(character_id)
    return make_response(jsonify(character), 200)


@bp.route("/characters/path/<string:char_path>", methods=["GET"])
def get_character_by_path(char_path: str) -> Response:
    """Gets a character by path."""
    character = db.select_character_by_path(char_path)
    return make_response(jsonify(character), 200)
