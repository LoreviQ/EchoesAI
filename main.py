"""
This is the main file that runs the application.
"""

import argparse

from dotenv import load_dotenv

import database as db
from app import App
from model import Model, ModelActual, ModelMocked


def main() -> None:
    """
    Entry point for the application.
    """
    load_dotenv()
    parser = argparse.ArgumentParser(description="Run the application.")
    parser.add_argument("--test", action="store_true", help="Enable test mode")
    args = parser.parse_args()
    db.create_db()  # Create the database if it doesn't exist
    model = ModelMocked("long") if args.test else ModelActual()
    manager = Model(model)
    app = App(manager)
    app.serve()


if __name__ == "__main__":
    main()
