"""
Module to hold server logic.
"""

from flask import Flask, make_response
from flask_cors import CORS


class App:
    """
    Class to manage the Flask app.
    """

    def __init__(self, port: int = 5000):
        self.app = Flask(__name__)
        CORS(self.app)
        self.port = port
        self._setup_routes()

    def _setup_routes(self) -> None:
        """
        Setup the routes for the Flask app.
        """

        @self.app.route("/readiness", methods=["GET"])
        def ready():
            return make_response("", 200)

    def serve(self) -> None:
        """
        Start the Flask app.
        """
        self.app.run(port=self.port)


if __name__ == "__main__":
    app_instance = App()
    app_instance.serve()
