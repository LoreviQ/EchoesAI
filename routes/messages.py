"""Routes for messages."""

from datetime import datetime, timedelta, timezone
from typing import Dict, List

from flask import Response, g, jsonify, make_response, request

import database as db

from .main import bp


@bp.route("/v1/threads/<int:thread_id>/messages", methods=["GET"])
def get_messages_by_thread(thread_id: int) -> Response:
    """Gets all messages for a thread."""
    try:
        db.select_thread(thread_id)
    except ValueError:
        return make_response("thread not found", 404)
    messages = db.select_messages_by_thread(thread_id)
    response: List[Dict[str, str]] = []
    for message in messages:
        response.append(
            {
                "id": message["id"],
                "content": message["content"],
                "role": message["role"],
                "timestamp": db.convert_dt_ts(message["timestamp"]),
            },
        )
    return make_response(jsonify(response), 200)


@bp.route("/v1/threads/<int:thread_id>/messages", methods=["POST"])
def post_message(thread_id: int) -> Response:
    """Posts a message to a thread."""
    try:
        db.select_thread(thread_id)
    except ValueError:
        return make_response("thread not found", 404)
    data = request.get_json()
    if not all(key in data for key in ("content", "role")):
        return make_response("missing required fields", 400)
    message = db.Message(
        thread=db.select_thread(thread_id),
        content=data["content"],
        role=data["role"],
    )
    db.insert_message(message)
    # Start the chatbot response cycle in a background thread
    g.trigger_response_cycle(thread_id)
    return make_response("", 200)


@bp.route("/v1/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id: int) -> Response:
    """Deletes a message, optionally with all more recent messages."""
    try:
        db.select_message(message_id)
    except ValueError:
        return make_response("message not found", 404)
    query_params = request.args.to_dict()
    if "recent" in query_params and query_params["recent"] == "true":
        db.delete_messages_more_recent(message_id)
    else:
        db.delete_message(message_id)
    return make_response("", 200)


@bp.route("/v1/threads/<int:thread_id>/message", methods=["GET"])
def get_response_now(thread_id: int) -> Response:
    """Gets a response for a thread immediately."""
    try:
        db.select_thread(thread_id)
    except ValueError:
        return make_response("thread not found", 404)
    # first attempt to apply scheduled message
    message_id = db.select_scheduled_message_id(thread_id)
    if message_id:
        message_patch = db.Message(
            id=message_id,
            timestamp=datetime.now(timezone.utc),
        )
        db.update_message(message_patch)
        return make_response("", 200)

    # if no scheduled message, trigger response cycle with no timedelta
    g.trigger_response_cycle(thread_id, timedelta())
    return make_response("", 200)
