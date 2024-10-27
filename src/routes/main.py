"""Sets up routing blueprint and holds miscellaneous routes."""

from flask import Blueprint, Response, g, jsonify, make_response, send_from_directory

bp = Blueprint("routes", __name__)


@bp.route("/v1/readiness", methods=["GET"])
def ready() -> Response:
    """Checks if the server is ready."""
    api_config = {
        "detatched": g.model is None,
    }
    return make_response(jsonify(api_config), 200)


@bp.route("/v1/images/<path:filename>", methods=["GET"])
def get_image(filename: str) -> Response:
    """Gets an image from the images directory."""
    return send_from_directory("../static/images", filename)
