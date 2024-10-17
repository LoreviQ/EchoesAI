"""
Module to hold server logic.
"""

from flask import Flask, Response, make_response
from flask_cors import CORS

from chatbot import Chatbot
from database import DB


class App:
    """
    Class to manage the Flask app.
    """

    def __init__(self, db_path: str, port: int = 5000):
        self.app = Flask(__name__)
        CORS(self.app)
        self.port = port
        self.db = DB(db_path)
        self._setup_routes()
        self.chatbot: Chatbot

    def _setup_routes(self) -> None:
        """
        Setup the routes for the Flask app.
        """

        @self.app.route("/readiness", methods=["GET"])
        def ready() -> Response:
            return make_response("", 200)

        @self.app.route("/chatbot/<int:thread_id>", methods=["POST"])
        def create_chatbot(thread_id: int) -> Response:
            self.chatbot = Chatbot(thread_id, self.db)
            return make_response("", 200)

    def serve(self) -> None:
        """
        Start the Flask app.
        """
        self.app.run(port=self.port)
