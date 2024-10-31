"""Sets up routing blueprint and holds miscellaneous routes."""

from flask import Blueprint, Response, g, make_response

import database as db

bp = Blueprint("routes", __name__)


@bp.route("/v1/readiness", methods=["GET"])
def ready() -> Response:
    """Checks if the server is ready."""
    return make_response("", 200)


@bp.route("/v1/detached", methods=["GET"])
def detached() -> Response:
    """Checks if the server is running in detached mode."""
    if g.detached:
        return make_response("True", 200)
    return make_response("False", 200)


def _create_query_params(query_params: dict[str, str]) -> db.QueryOptions:
    options = db.QueryOptions()
    if "limit" in query_params:
        options["limit"] = int(query_params["limit"])
    if "orderby" in query_params:
        options["orderby"] = query_params["orderby"]
    if "order" in query_params:
        options["order"] = query_params["order"]
    return options
