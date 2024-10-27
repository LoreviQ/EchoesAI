"""Sets up routing blueprint and holds miscellaneous routes."""

from flask import Blueprint, Response, g, make_response, send_from_directory

bp = Blueprint("routes", __name__)


@bp.route("/v1/readiness", methods=["GET"])
def ready() -> Response:
    """Checks if the server is ready."""
    return make_response("", 200)


@bp.route("/v1/images/<path:filename>", methods=["GET"])
def get_image(filename: str) -> Response:
    """Gets an image from the images directory."""
    return send_from_directory("../static/images", filename)


@bp.route("/v1/detatched", methods=["GET"])
def detatched() -> Response:
    """Checks if the server is running in detatched mode."""
    if g.detatched:
        return make_response("", 200)
    return make_response("", 400)
