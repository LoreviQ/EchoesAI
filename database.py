"""
This module contains the class to manage the database and other database-related functions.
"""

import sqlite3
from datetime import datetime
from sqlite3 import Connection, Cursor
from typing import Callable, Dict, List, Tuple


class DB:
    """
    Class to manage the database.
    """

    def __init__(self, db_path: str = "database.db") -> None:
        self.db_path = db_path
        self.queries: Dict[str, str] = {
            "post_message": "INSERT INTO messages (thread, content, role) VALUES (?, ?, ?)",
            "post_message_with_timestamp": "INSERT INTO messages (thread, content, role, timestamp) VALUES (?, ?, ?, ?)",
            "get_messages": "SELECT id, content, role, timestamp FROM messages",
            "get_messages_by_thread": "SELECT id, content, role, timestamp FROM messages WHERE thread = ?",
            "post_thread": "INSERT INTO threads (user, chatbot) VALUES (?, ?) RETURNING id",
            "get_thread": "SELECT user, chatbot, phase FROM threads WHERE id = ?",
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

    def _setup(self) -> Tuple[Connection, Cursor, Callable[[], None]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        def close() -> None:
            cursor.close()
            conn.close()

        return conn, cursor, close

    def post_thread(self, user: str, chatbot: str) -> int:
        """
        Insert a new thread into the database returning the thread id.
        """
        conn, cursor, close = self._setup()
        cursor.execute(
            self.queries["post_thread"],
            (user, chatbot),
        )
        result = cursor.fetchone()[0]
        conn.commit()
        close()
        return result

    def get_thread(self, thread_id: int) -> Tuple[str, str, str]:
        """
        Get the user and chatbot for a thread.
        """
        _, cursor, close = self._setup()
        cursor.execute(
            self.queries["get_thread"],
            (thread_id,),
        )
        result = cursor.fetchone()
        close()
        if result:
            return result
        raise ValueError("Thread not found")

    def get_latest_thread(self, user: str, chatbot: str) -> int:
        """
        Get the latest thread for a user and chatbot.
        """
        _, cursor, close = self._setup()
        cursor.execute(
            self.queries["get_latest_thread"],
            (user, chatbot),
        )
        result = cursor.fetchone()
        close()
        if result[0]:
            return result[0]
        return 0

    def get_threads_by_user(self, user: str) -> List[Tuple[int, str]]:
        """
        Get all threads for a user.
        """
        _, cursor, close = self._setup()
        cursor.execute(
            self.queries["get_threads_by_user"],
            (user,),
        )
        result = cursor.fetchall()
        close()
        return result

    def post_message(
        self, thread: int, content: str, role: str, timestamp: datetime | None = None
    ) -> None:
        """
        Insert a message into the database.
        """
        conn, cursor, close = self._setup()
        if timestamp:
            formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                self.queries["post_message_with_timestamp"],
                (thread, content, role, formatted_time),
            )
        else:
            cursor.execute(
                self.queries["post_message"],
                (thread, content, role),
            )
        conn.commit()
        close()

    def get_messages(self) -> List[Tuple[int, str, str, str]]:
        """
        Get all messages from the database.
        """
        _, cursor, close = self._setup()
        cursor.execute(self.queries["get_messages"])
        result = cursor.fetchall()
        close()
        return result

    def get_messages_by_thread(self, thread_id: int) -> List[Tuple[int, str, str, str]]:
        """
        Get all messages from the database.
        """
        _, cursor, close = self._setup()
        cursor.execute(self.queries["get_messages_by_thread"], (thread_id,))
        result = cursor.fetchall()
        close()
        return result

    def delete_messages_more_recent(self, message_id: int) -> None:
        """
        Delete selected message and all more recent messages.
        """
        conn, cursor, close = self._setup()
        cursor.execute(
            """
                DELETE FROM messages
                WHERE id = ?
                OR (thread = (SELECT thread FROM messages WHERE id = ?)
                    AND timestamp > (SELECT timestamp FROM messages WHERE id = ?))
            """,
            (message_id, message_id, message_id),
        )
        conn.commit()
        close()

    def apply_scheduled_message(self, thread_id: int) -> bool:
        """
        Checks the DB for any scheduled messages
        and applies them (changed datetime to timestamp).
        If there are no scheduled messages, returns False.
        """
        conn, cursor, close = self._setup()
        cursor.execute(
            """
            UPDATE messages
            SET timestamp = CURRENT_TIMESTAMP
            WHERE thread = :thread_id AND timestamp > CURRENT_TIMESTAMP
            """,
            (thread_id,),
        )
        if cursor.rowcount != 1:
            close()
            return False
        conn.commit()
        close()
        return True
