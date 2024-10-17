"""
This module contains the class to manage the database and other database-related functions.
"""

import sqlite3
from typing import Dict, List, Tuple


class DB:
    """
    Class to manage the database.
    """

    def __init__(self, db_path: str = "database.db") -> None:
        self.conn = sqlite3.connect(db_path)
        self.queries: Dict[str, str] = {
            "post_message": "INSERT INTO messages (thread, content, role) VALUES (?, ?, ?)",
            "get_messages": "SELECT * FROM messages",
            "get_messages_by_thread": "SELECT * FROM messages WHERE thread = ?",
            "post_thread": "INSERT INTO threads (user, chatbot) VALUES (?, ?) RETURNING id",
            "get_thread": "SELECT user, chatbot FROM threads WHERE id = ?",
            "get_latest_thread": "SELECT MAX(id) FROM threads WHERE user = ? AND chatbot = ?",
        }
        self._create_db()

    def _create_db(self) -> None:
        """
        Create the database with the schema if it doesn't exist.
        """
        with open("./sql/schema.sql", "r", encoding="utf-8") as file:
            schema = file.read()
        with self.conn:
            self.conn.executescript(schema)
            self.conn.commit()

    def post_thread(self, user: str, chatbot: str) -> int:
        """
        Insert a new thread into the database returning the thread id.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            self.queries["post_thread"],
            (user, chatbot),
        )
        result = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return result

    def get_thread(self, thread_id: int) -> Tuple[str, str]:
        """
        Get the user and chatbot for a thread.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            self.queries["get_thread"],
            (thread_id,),
        )
        result = cursor.fetchone()
        cursor.close()
        if result:
            return result
        raise ValueError("Thread not found")

    def get_latest_thread(self, user: str, chatbot: str) -> int:
        """
        Get the latest thread for a user and chatbot.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            self.queries["get_latest_thread"],
            (user, chatbot),
        )
        result = cursor.fetchone()
        cursor.close()
        if result[0]:
            return result[0]
        return 0

    def post_message(self, thread: int, content: str, role: str) -> None:
        """
        Insert a message into the database.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            self.queries["post_message"],
            (thread, content, role),
        )
        self.conn.commit()
        cursor.close()

    def get_messages(self) -> List[Tuple[int, str, str, str, str]]:
        """
        Get all messages from the database.
        """
        cursor = self.conn.cursor()
        cursor.execute(self.queries["get_messages"])
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_messages_by_thread(
        self, thread_id: int
    ) -> List[Tuple[int, str, str, str, str]]:
        """
        Get all messages from the database.
        """
        cursor = self.conn.cursor()
        cursor.execute(self.queries["get_messages_by_thread"], (thread_id,))
        result = cursor.fetchall()
        cursor.close()
        return result
