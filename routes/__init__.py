from flask import Flask

# Import all route files to ensure their routes are registered with the Blueprint
from . import characters, events, messages, posts, threads, users
from .main import bp


def register_routes(app: Flask) -> None:
    """Register all routes with the Flask app."""
    app.register_blueprint(bp)
