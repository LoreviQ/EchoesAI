"""
Module to hold server logic.
"""

from flask import Flask, Response, make_response, request
from flask_cors import CORS

from chatbot import Chatbot


class App:
    """
    Class to manage the Flask app.
    """

    def __init__(self, port: int = 5000):
        self.app = Flask(__name__)
        CORS(self.app)
        self.port = port
        self._setup_routes()
        self.chatbot: Chatbot

    def _setup_routes(self) -> None:
        """
        Setup the routes for the Flask app.
        """

        @self.app.route("/readiness", methods=["GET"])
        def ready() -> Response:
            return make_response("", 200)

        @self.app.route("/chatbot/new", methods=["POST"])
        def new_chatbot() -> Response:
            data = request.json
            if data is None:
                return make_response("Invalid JSON", 400)
            username = data["username"]
            character = data["character"]
            self.create_chatbot(username, character)
            return make_response("", 200)

    def create_chatbot(self, username: str, character: str) -> None:
        """
        Create a chatbot instance.
        """
        self.chatbot = Chatbot(username, character)

    def serve(self) -> None:
        """
        Start the Flask app.
        """
        self.app.run(port=self.port)


if __name__ == "__main__":
    app_instance = App()
    app_instance.create_chatbot("Oliver", "ophelia")
    app_instance.serve()
