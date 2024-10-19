"""
Module to hold server logic.
"""

import threading
from datetime import timedelta

from flask import Flask, Response, jsonify, make_response, request
from flask_cors import CORS

from chatbot import Chatbot
from database import DB
from model import Model


class App:
    """
    Class to manage the Flask app.
    """

    def __init__(self, db_path: str, model: Model, port: int = 5000):
        self.app = Flask(__name__)
        CORS(self.app)
        self.port = port
        self.db = DB(db_path)
        self._setup_routes()
        self.model = model
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
            return make_response(jsonify(threads), 200)

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
            # Start the chatbot response cycle in a background thread
            background_thread = threading.Thread(
                target=self._trigger_response_cycle, args=(thread_id,)
            )
            background_thread.start()
            return make_response("", 200)

        @self.app.route("/messages/<int:message_id>", methods=["DELETE"])
        def delete_messages_more_recent(message_id: int) -> Response:
            self.db.delete_messages_more_recent(message_id)
            return make_response("", 200)

        @self.app.route("/threads/<int:thread_id>/messages/new", methods=["GET"])
        def get_response_now(thread_id: int) -> Response:
            # first attempt to apply scheduled message
            success = self.db.apply_scheduled_message(thread_id)
            if success:
                return make_response("", 200)
            # if no scheduled message, trigger response cycle with no timedelta
            self._trigger_response_cycle(thread_id, timedelta())
            return make_response("", 200)

    def serve(self) -> None:
        """
        Start the Flask app.
        """
        self.app.run(port=self.port)

    def _trigger_response_cycle(
        self, thread_id: int, duration: timedelta | None = None
    ) -> None:
        self.chatbot = Chatbot(thread_id, self.db, self.model)
        self.chatbot.response_cycle(duration)
