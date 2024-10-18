"""
Module to hold server logic.
"""

from flask import Flask, Response, jsonify, make_response, request
from flask_cors import CORS

from chatbot import Chatbot
from database import DB
from model import MockedModel, Model, new_model


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
        self.model: Model | MockedModel | None = None
        self.chatbot: Chatbot

    def _setup_routes(self) -> None:
        """
        Setup the routes for the Flask app.
        """

        @self.app.route("/readiness", methods=["GET"])
        def ready() -> Response:
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

        @self.app.route("/threads/<int:thread_id>/messages", methods=["GET"])
        def get_messages_by_thread(thread_id: int) -> Response:
            messages = self.db.get_messages_by_thread(thread_id)
            messages_dict = [
                {"message_id": m[0], "content": m[1], "role": m[2], "timestamp": m[3]}
                for m in messages
            ]
            return make_response(jsonify(messages_dict), 200)

        @self.app.route("/threads/<int:thread_id>/messages", methods=["POST"])
        def post_message(thread_id: int) -> Response:
            data = request.get_json()
            content = data["content"]
            role = data["role"]
            self.db.post_message(thread_id, content, role)
            return make_response("", 200)

        @self.app.route("/messages/<int:message_id>", methods=["DELETE"])
        def delete_messages_more_recent(message_id: int) -> Response:
            self.db.delete_messages_more_recent(message_id)
            return make_response("", 200)

    def serve(self) -> None:
        """
        Start the Flask app.
        """
        self.app.run(port=self.port)

    def load_model(self, mocked: bool = False) -> None:
        """
        Load the model for the chatbot.
        Model is loaded once and passed to the chatbot instance.
        This prevents excessive loading of the model.
        """
        self.model = new_model(mocked)

    def _new_chatbot(self, thread_id: int) -> Chatbot:
        if not self.model:
            return make_response("Model not loaded", 400)
        return Chatbot(thread_id, self.db, self.model)
