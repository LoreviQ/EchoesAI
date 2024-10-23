"""
Module to hold server logic.
"""

import atexit
import threading
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask, Response, jsonify, make_response, request, send_from_directory
from flask_cors import CORS

import database as db
from chatbot import generate_event, generate_social_media_post, response_cycle
from model import Model


class App:
    """
    Class to manage the Flask app.
    """

    def __init__(self, model: Model, port: int = 5000):
        self.app = Flask(__name__)
        CORS(self.app)
        self.port = port
        self.model = model
        db.create_db()
        self._setup_routes()
        self._schedule_events()

    def _setup_routes(self) -> None:
        """
        Setup the routes for the Flask app.
        """

        @self.app.route("/readiness", methods=["GET"])
        def ready() -> Response:
            return make_response("", 200)

        @self.app.route("/images/<path:filename>", methods=["GET"])
        def get_image(filename: str) -> Response:
            return send_from_directory("static/images", filename)

        @self.app.route("/threads/new", methods=["POST"])
        def new_thread() -> Response:
            data = request.get_json()
            username = data["username"]
            character = data["character"]
            thread_id = db.insert_thread(username, character)
            return make_response(str(thread_id), 200)

        @self.app.route("/threads/<string:username>", methods=["GET"])
        def get_threads_by_user(username: str) -> Response:
            threads = db.select_threads_by_user(username)
            return make_response(jsonify(threads), 200)

        @self.app.route("/threads/<int:thread_id>/messages", methods=["GET"])
        def get_messages_by_thread(thread_id: int) -> Response:
            messages = db.select_messages_by_thread(thread_id)
            response: List[Dict[str, Any]] = []
            for message in messages:
                response.append(
                    {
                        "id": message["id"],
                        "content": message["content"],
                        "role": message["role"],
                        "timestamp": db.convert_dt_ts(message["timestamp"]),
                    },
                )
            return make_response(jsonify(response), 200)

        @self.app.route("/threads/<int:thread_id>/messages", methods=["POST"])
        def post_message(thread_id: int) -> Response:
            data = request.get_json()
            message = db.Message(
                thread=db.select_thread(thread_id),
                content=data["content"],
                role=data["role"],
            )
            db.insert_message(message)
            # Start the chatbot response cycle in a background thread
            background_thread = threading.Thread(
                target=self._trigger_response_cycle, args=(thread_id,)
            )
            background_thread.start()
            return make_response("", 200)

        @self.app.route("/messages/<int:message_id>", methods=["DELETE"])
        def delete_messages_more_recent(message_id: int) -> Response:
            db.delete_messages_more_recent(message_id)
            return make_response("", 200)

        @self.app.route("/threads/<int:thread_id>/messages/new", methods=["GET"])
        def get_response_now(thread_id: int) -> Response:
            # first attempt to apply scheduled message
            message_id = db.select_scheduled_message_id(thread_id)
            if message_id:
                message_patch = db.Message(
                    id=message_id,
                    timestamp=datetime.now(timezone.utc),
                )
                db.update_message(message_patch)
                return make_response("", 200)

            # if no scheduled message, trigger response cycle with no timedelta
            self._trigger_response_cycle(thread_id, timedelta())
            return make_response("", 200)

        @self.app.route("/events/<int:character>", methods=["GET"])
        def get_events_by_character(character: int) -> Response:
            events = db.events.select_events_by_character(character)
            response: List[Dict[str, Any]] = []
            for event in events:
                response.append(
                    {
                        "id": event["id"],
                        "type": event["type"],
                        "content": event["content"],
                        "timestamp": db.convert_dt_ts(event["timestamp"]),
                    },
                )
            return make_response(jsonify(response), 200)

        @self.app.route("/posts/<int:character>", methods=["GET"])
        def get_posts_by_character(character: int) -> Response:
            posts = db.posts.get_posts_by_character(character)
            response: List[Dict[str, Any]] = []
            for post in posts:
                response.append(
                    {
                        "id": post["id"],
                        "timestamp": db.convert_dt_ts(post["timestamp"]),
                        "description": post["description"],
                        "prompt": post["prompt"],
                        "caption": post["caption"],
                        "image_path": post["image_path"],
                    },
                )
            return make_response(jsonify(response), 200)

        @self.app.route("/characters/new", methods=["POST"])
        def new_character() -> Response:
            data = request.get_json()
            character = db.Character(
                name=data["name"],
                path_name=data["path_name"],
                description=data["description"],
                age=data["age"],
                height=data["height"],
                personality=data["personality"],
                appearance=data["appearance"],
                loves=data["loves"],
                hates=data["hates"],
                details=data["details"],
                scenario=data["scenario"],
                important=data["important"],
                initial_message=data["initial_message"],
                favorite_colour=data["favorite_colour"],
                phases=False,
                img_gen=data["img_gen"],
                model=data["model"],
                global_positive=data["global_positive"],
                global_negative=data["global_negative"],
            )
            db.insert_character(character)
            return make_response(str(data["path_name"]), 200)

        @self.app.route("/characters/<int:character_id>", methods=["GET"])
        def get_character(character_id: int) -> Response:
            character = db.select_character(character_id)
            return make_response(jsonify(character), 200)

        # TODO Schedule this later, it's only a route for testing
        @self.app.route("/img_gen_start")
        def img_gen_start() -> Response:
            generate_social_media_post(self.model, 1)
            return make_response("", 200)

    def _schedule_events(self) -> None:
        # TODO: extend to other chatbots and event types
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=generate_event,
            trigger=CronTrigger(minute="0,30"),
            args=(
                self.model,
                1,
                "event",
            ),
        )
        scheduler.add_job(
            func=generate_event,
            trigger=CronTrigger(minute="15,45"),
            args=(
                self.model,
                1,
                "thought",
            ),
        )
        if not self.model.mocked:
            scheduler.add_job(
                func=generate_social_media_post,
                trigger=CronTrigger(minute="0"),
                args=(
                    self.model,
                    1,
                ),
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
        response_cycle(self.model, thread_id, duration)
