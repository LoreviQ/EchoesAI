"""Sets up routing blueprint and holds miscellaneous routes."""

from datetime import timedelta

from flask import Blueprint, Response, g, make_response, request
from google.cloud import storage

import database as db

bp = Blueprint("routes", __name__)
BUCKET_NAME = "echoesai-public-images"


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


@bp.route("/v1/get-signed-url", methods=["POST"])
def get_signed_url() -> Response:
    """Gets a GCS signed URL to upload an image to the project bucket."""
    data = request.get_json()
    if not all(key in data for key in ("file_name", "file_type")):
        return make_response("Missing required fields", 400)
    try:
        signed_url = _generate_gcs_signed_url(data["file_name"], data["file_type"])
        return make_response(signed_url, 200)
    except ValueError as e:
        return make_response(str(e), 400)


def _create_query_params(query_params: dict[str, str]) -> db.QueryOptions:
    options = db.QueryOptions()
    if "limit" in query_params:
        options["limit"] = int(query_params["limit"])
    if "offset" in query_params:
        options["offset"] = int(query_params["offset"])
    if "orderby" in query_params:
        options["orderby"] = query_params["orderby"]
    if "order" in query_params:
        options["order"] = query_params["order"]
    return options


def _generate_gcs_signed_url(file_name: str, file_type: str) -> str:
    """Generates a signed URL for a file in the GCS bucket."""
    if file_type not in ("jpg", "jpeg", "png"):
        raise ValueError("Invalid file type. Must be one of 'jpg', 'jpeg', or 'png'.")
    blob_name = f"{file_name}.{file_type}"
    expiration_time = timedelta(hours=1)  # URL valid for 1 hour
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    content_type = f"image/{file_type}"
    signed_url = blob.generate_signed_url(
        version="v4",
        expiration=expiration_time,
        method="PUT",
        content_type=content_type,
    )
    return signed_url
