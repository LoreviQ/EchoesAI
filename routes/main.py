"""Sets up routing blueprint and holds miscellaneous routes."""

from flask import Blueprint, Response, make_response, send_from_directory

bp = Blueprint("routes", __name__)


@bp.route("/readiness", methods=["GET"])
def ready() -> Response:
    """Checks if the server is ready."""
    return make_response("", 200)


@bp.route("/images/<path:filename>", methods=["GET"])
def get_image(filename: str) -> Response:
    """Gets an image from the images directory."""
    return send_from_directory("static/images", filename)
