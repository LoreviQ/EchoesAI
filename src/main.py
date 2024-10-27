"""
This is the main file that runs the application.
"""

import argparse

from dotenv import load_dotenv

import database as db
from app import App
from chatbot import new_model


def main() -> None:
    """
    Entry point for the application.
    """
    load_dotenv()
    parser = argparse.ArgumentParser(description="Run the application.")
    parser.add_argument("--test", action="store_true", help="Use a mocked model")
    parser.add_argument(
        "--detatched",
        action="store_true",
        help="Does not load a model - Used to host api without enabling generative ai",
    )
    args = parser.parse_args()
    db.create_db()  # Create the database if it doesn't exist
    if args.detatched:
        model = None
    else:
        model = new_model(mocked=args.test)
    app = App(model, detatched=args.detatched)
    app.serve()


if __name__ == "__main__":
    main()
