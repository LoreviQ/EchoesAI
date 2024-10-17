"""
Module to hold server logic.
"""

from flask import Flask, Response, jsonify, make_response, request
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

        @self.app.route("/threads/new", methods=["POST"])
        def new_thread() -> Response:
            data = request.get_json()
            username = data["username"]
            character = data["character"]
            thread_id = self.db.post_thread(username, character)
            return make_response(str(thread_id), 200)

        @self.app.route("/threads/<string:username>", methods=["GET"])
        def get_threads_by_user(username: str) -> Response:
            threads = self.db.get_threads_by_user(username)
            threads_dict = [{"id": t[0], "character": t[1]} for t in threads]

            return make_response(jsonify(threads_dict), 200)

        @self.app.route("/thread/<int:thread_id>/messages", methods=["GET"])
        def get_messages_by_thread(thread_id: int) -> Response:
            messages = self.db.get_messages_by_thread(thread_id)
            messages_dict = [
                {"content": m[0], "role": m[1], "timestamp": m[2]} for m in messages
            ]
            return make_response(jsonify(messages_dict), 200)

    def serve(self) -> None:
        """
        Start the Flask app.
        """
        self.app.run(port=self.port)
