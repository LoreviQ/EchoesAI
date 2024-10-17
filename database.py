"""
This module contains the class to manage the database and other database-related functions.
"""

import sqlite3
from typing import Dict


class DB:
    """
    Class to manage the database.
    """

    def __init__(self) -> None:
        # Connect to the database
        self.conn = sqlite3.connect("database.db")
        self.cursor = self.conn.cursor()

        # Create the schema if it doesn't exist
        with open("./sql/schema.sql", "r", encoding="utf-8") as file:
            schema = file.read()
        self.cursor.executescript(schema)
        self.conn.commit()
        self.queries: Dict[str, str] = {
            "post_message": "INSERT INTO messages (user, chatbot, content) VALUES (?, ?, ?)"
        }

    def post_message(self, user: str, chatbot: str, content: str) -> None:
        """
        Insert a message into the database.
        """
        self.cursor.execute(
            self.queries["post_message"],
            (user, chatbot, content),
        )
        self.conn.commit()


if __name__ == "__main__":
    db = DB()
