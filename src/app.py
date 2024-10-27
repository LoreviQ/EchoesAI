"""
Module to hold server logic.
"""

import threading
from datetime import timedelta

from flask import Flask, g
from flask_cors import CORS

import routes
from chatbot import Model, response_cycle, schedule_events


class App:
    """
    Class to manage the Flask app.
    """

    def __init__(self, model: Model, port: int = 5000, detatched: bool = False) -> None:
        self.port = port
        self.detatched = detatched
        self.app = Flask(__name__)
        CORS(self.app)
        routes.register_routes(self.app)
        self._setup_before_request()
        self.model = None
        if not detatched:
            self.model = model
            schedule_events(model)

    def _setup_before_request(self) -> None:
        @self.app.before_request
        def before_request() -> None:
            g.detatched = self.detatched
            g.trigger_response_cycle = self.trigger_response_cycle

    def serve(self) -> None:
        """
        Start the Flask app.
        """
        self.app.run(port=self.port)

    def trigger_response_cycle(
        self, thread_id: int, duration: timedelta | None = None
    ) -> None:
        """Start the chatbot response cycle in a background thread."""
        if self.detatched:
            print("App is in detatched mode. Cannot trigger response cycle.")
            return
        thread = threading.Thread(
            target=response_cycle, args=(self.model, thread_id, duration)
        )
        thread.start()
