"""
This is the main file that runs the application.
"""

import argparse

from app import App


def main() -> None:
    """
    Entry point for the application.
    """
    parser = argparse.ArgumentParser(description="Run the application.")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    app = App("database.db")
    app.load_model(args.debug)
    app.serve()


if __name__ == "__main__":
    main()
