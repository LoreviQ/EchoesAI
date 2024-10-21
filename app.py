"""
Module to hold server logic.
"""

import atexit
import threading
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask, Response, jsonify, make_response, request
from flask_cors import CORS

from chatbot import Chatbot
from database import DB, convert_dt_ts
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
        self.model = model
        self._setup_routes()
        self._schedule_events()

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
            response: List[Dict[str, Any]] = []
            for message in messages:
                response.append(
                    {
                        "id": message["id"],
                        "content": message["content"],
                        "role": message["role"],
                        "timestamp": convert_dt_ts(message["timestamp"]),
                    },
                )
            return make_response(jsonify(response), 200)

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
            message_id = self.db.get_scheduled_message(thread_id)
            if message_id:
                self.db.update_message(message_id, datetime.now(timezone.utc))
                return make_response("", 200)

            # if no scheduled message, trigger response cycle with no timedelta
            self._trigger_response_cycle(thread_id, timedelta())
            return make_response("", 200)

        @self.app.route("/events/<string:character>", methods=["GET"])
        def get_events_by_character(character: str) -> Response:
            events = self.db.get_events_by_chatbot(character)
            response: List[Dict[str, Any]] = []
            for event in events:
                response.append(
                    {
                        "id": event["id"],
                        "type": event["type"],
                        "content": event["content"],
                        "timestamp": convert_dt_ts(event["timestamp"]),
                    },
                )
            return make_response(jsonify(response), 200)

    def _schedule_events(self) -> None:
        # TODO: extend to other chatbots and event types
        scheduler = BackgroundScheduler()
        chatbot = Chatbot("ophelia", self.db, self.model)
        scheduler.add_job(
            func=chatbot.generate_event,
            trigger=CronTrigger(minute="0,30"),
            args=("event",),
        )
        scheduler.add_job(
            func=chatbot.generate_event,
            trigger=CronTrigger(minute="15,45"),
            args=("thought",),
        )
        scheduler.start()
        atexit.register(scheduler.shutdown)

    def serve(self) -> None:
        """
        Start the Flask app.
        """
        self.app.run(port=self.port)

    def _trigger_response_cycle(
        self, thread_id: int, duration: timedelta | None = None
    ) -> None:
        thread = self.db.get_thread(thread_id)
        chatbot = Chatbot(thread["chatbot"], self.db, self.model)
        chatbot.response_cycle(thread_id, duration)
