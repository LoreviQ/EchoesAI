"""Routes for events."""

from typing import Dict, List

from flask import Response, jsonify, make_response

import database as db

from .main import bp


@bp.route("/events/<string:char_path>", methods=["GET"])
def get_events_by_character(char_path: str) -> Response:
    """Gets all events for a character."""
    character = db.select_character_by_path(char_path)
    assert character["id"]
    events = db.events.select_events_by_character(character["id"])
    response: List[Dict[str, str]] = []
    for event in events:
        response.append(
            {
                "id": event["id"],
                "type": event["type"],
                "content": event["content"],
                "timestamp": db.convert_dt_ts(event["timestamp"]),
            },
        )
    return make_response(jsonify(response), 200)
