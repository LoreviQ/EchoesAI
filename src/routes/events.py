"""Routes for events."""

from flask import Response, jsonify, make_response, request

import database as db

from .main import bp


@bp.route("/v1/events", methods=["GET"])
def get_events() -> Response:
    """Get events, optionally with a query."""
    query_params = request.args.to_dict()
    try:
        event_query = _create_event_query_params(query_params)
    except ValueError:
        return make_response(jsonify([]), 200)
    events = db.select_events(event_query)
    return make_response(jsonify(events), 200)


def _create_event_query_params(query_params: dict[str, str]) -> db.Event:
    event_query = db.Event()
    # basic params
    if "id" in query_params:
        event_query["id"] = int(query_params["id"])
    if "char_id" in query_params:
        event_query["char_id"] = int(query_params["char_id"])
    if "type" in query_params:
        event_query["type"] = query_params["type"]
    if "content" in query_params:
        event_query["content"] = query_params["content"]
    # custom params
    if "char_path" in query_params:
        character = db.select_character(query_params["char_path"])
        event_query["char_id"] = character["id"]
    return event_query
