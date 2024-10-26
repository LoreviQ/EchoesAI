"""Routes for events."""

from typing import Dict, List

from flask import Response, jsonify, make_response, request

import database as db

from .main import bp


@bp.route("/v1/events", methods=["GET"])
def get_events() -> Response:
    """Get events, optionally with a query."""
    query_params = request.args.to_dict()
    event_query = db.Event(**query_params)
    if "char_path" in query_params:
        try:
            char_id = db.select_characters(
                db.Character(path_name=query_params["char_path"])
            )[0]["id"]
            event_query["character"] = char_id
        except KeyError:
            return make_response(b"character not found", 404)

    events = db.select_events(event_query)
    response: List[Dict[str, str]] = []
    for event in events:
        response.append(
            {
                "id": event["id"],
                "timestamp": db.convert_dt_ts(event["timestamp"]),
                "character": event["character"],
                "type": event["type"],
                "content": event["content"],
            },
        )
    return make_response(jsonify(response), 200)
