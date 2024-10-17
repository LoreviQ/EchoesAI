"""
This module contains the class to manage the database and other database-related functions.
"""

import sqlite3
from typing import Dict, List, Optional, Tuple


class DB:
    """
    Class to manage the database.
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        # Connect to the database
        if db_path:
            self.conn = sqlite3.connect(db_path)
        else:
            self.conn = sqlite3.connect("database.db")
        self.cursor = self.conn.cursor()

        # Create the schema if it doesn't exist
        with open("./sql/schema.sql", "r", encoding="utf-8") as file:
            schema = file.read()
        self.cursor.executescript(schema)
        self.conn.commit()
        self.queries: Dict[str, str] = {
            "post_message": "INSERT INTO messages (user, chatbot, content) VALUES (?, ?, ?)",
            "get_messages": "SELECT * FROM messages",
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

    def get_messages(self) -> List[Tuple[int, str, str, str, str]]:
        """
        Get all messages from the database.
        """
        self.cursor.execute(self.queries["get_messages"])
        return self.cursor.fetchall()


if __name__ == "__main__":
    db = DB()
    db.post_message("user", "chatbot", "test message")
    db.post_message("user2", "chatbot2", "test message2")
    messages = db.get_messages()
    print(messages)
