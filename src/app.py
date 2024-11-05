"""
This is the main file that runs the application.
"""

import argparse
import importlib
import os
import threading
from datetime import timedelta

from flask import Flask, g
from flask_cors import CORS

import routes
from database import create_db


class App:
    """
    Class to manage the Flask app.
    """

    def __init__(self, mocked: bool = False, detached: bool = False) -> None:
        self.port = int(os.getenv("PORT", "5000"))
        self.app = Flask(__name__)
        self.detached = detached
        CORS(self.app)
        routes.register_routes(self.app)
        self._setup_before_request()
        self.model = None
        self.new_model = None
        self.response_cycle = None
        self.schedule_events = None
        if not self.detached:
            self._import_functions()
            assert self.new_model is not None
            assert self.schedule_events is not None
            self.model = self.new_model(mocked=mocked)
            self.schedule_events(self.model)

    def _setup_before_request(self) -> None:
        @self.app.before_request
        def before_request() -> None:
            g.detached = self.detached
            g.trigger_response_cycle = self.trigger_response_cycle

    def serve(self) -> None:
        """
        Start the Flask app.
        """
        self.app.run(host="0.0.0.0", port=self.port)

    def trigger_response_cycle(
        self, thread_id: int, duration: timedelta | None = None
    ) -> None:
        """Start the chatbot response cycle in a background thread."""
        if self.detached:
            print("App is in detached mode. Cannot trigger response cycle.")
            return
        thread = threading.Thread(
            target=self.response_cycle, args=(self.model, thread_id, duration)
        )
        thread.start()

    def _import_functions(self) -> None:
        """
        Import the chatbot functions if necessary.
        """
        if (
            self.new_model is not None
            and self.response_cycle is not None
            and self.schedule_events is not None
        ):
            return
        module = importlib.import_module("chatbot")
        self.new_model = module.new_model
        self.response_cycle = module.response_cycle
        self.schedule_events = module.schedule_events


def main() -> None:
    """
    Entry point for the application.
    """
    create_db()
    parser = argparse.ArgumentParser(description="Run the application.")
    parser.add_argument("--test", action="store_true", help="Use a mocked model")
    args = parser.parse_args()
    detached = os.getenv("DETACHED_MODE", "false").lower() == "true"
    if detached:
        print("Running in detached mode. Generative AI is disabled.")
    app = App(mocked=args.test, detached=detached)
    app.serve()


if __name__ == "__main__":
    main()
