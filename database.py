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
        self.db_path = db_path
        self.queries: Dict[str, str] = {
            "post_message": "INSERT INTO messages (thread, content, role) VALUES (?, ?, ?)",
            "get_messages": "SELECT content, role, timestamp FROM messages",
            "get_messages_by_thread": "SELECT content, role, timestamp FROM messages WHERE thread = ?",
            "post_thread": "INSERT INTO threads (user, chatbot) VALUES (?, ?) RETURNING id",
            "get_thread": "SELECT user, chatbot FROM threads WHERE id = ?",
            "get_threads_by_user": "SELECT id, chatbot FROM threads WHERE user = ?",
            "get_latest_thread": "SELECT MAX(id) FROM threads WHERE user = ? AND chatbot = ?",
        }
        self._create_db()

    def _create_db(self) -> None:
        """
        Create the database with the schema if it doesn't exist.
        """
        conn = sqlite3.connect(self.db_path)
        with open("./sql/schema.sql", "r", encoding="utf-8") as file:
            schema = file.read()
        with conn:
            conn.executescript(schema)
            conn.commit()
        conn.close()

    def post_thread(self, user: str, chatbot: str) -> int:
        """
        Insert a new thread into the database returning the thread id.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            self.queries["post_thread"],
            (user, chatbot),
        )
        result = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return result

    def get_thread(self, thread_id: int) -> Tuple[str, str]:
        """
        Get the user and chatbot for a thread.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            self.queries["get_thread"],
            (thread_id,),
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return result
        raise ValueError("Thread not found")

    def get_latest_thread(self, user: str, chatbot: str) -> int:
        """
        Get the latest thread for a user and chatbot.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            self.queries["get_latest_thread"],
            (user, chatbot),
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result[0]:
            return result[0]
        return 0

    def get_threads_by_user(self, user: str) -> List[Tuple[int, str]]:
        """
        Get all threads for a user.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            self.queries["get_threads_by_user"],
            (user,),
        )
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    def post_message(self, thread: int, content: str, role: str) -> None:
        """
        Insert a message into the database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            self.queries["post_message"],
            (thread, content, role),
        )
        conn.commit()
        cursor.close()
        conn.close()

    def get_messages(self) -> List[Tuple[str, str, str]]:
        """
        Get all messages from the database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(self.queries["get_messages"])
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    def get_messages_by_thread(self, thread_id: int) -> List[Tuple[str, str, str]]:
        """
        Get all messages from the database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(self.queries["get_messages_by_thread"], (thread_id,))
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
