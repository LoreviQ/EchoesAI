"""
This module contains the class to manage the database and other database-related functions.
"""

import sqlite3
from datetime import datetime, timezone
from sqlite3 import Connection, Cursor
from typing import Callable, Dict, List, Tuple, TypedDict

queries: Dict[str, str] = {
    # MESSAGES
    "get_scheduled_message": "SELECT id FROM messages WHERE thread = ? AND timestamp > CURRENT_TIMESTAMP",
    "get_messages": "SELECT m.id, m.content, m.role, m.timestamp, t.user, t.chatbot FROM messages as m JOIN threads as t ON m.thread = t.id",
    "get_messages_by_thread": "SELECT m.id, m.content, m.role, m.timestamp, t.user, t.chatbot FROM messages as m JOIN threads as t ON m.thread = t.id WHERE thread = ?",
    "get_messages_by_character": "SELECT m.id, m.content, m.role, m.timestamp, t.user, t.chatbot FROM messages as m JOIN threads as t ON m.thread = t.id WHERE t.chatbot = ?",
    "post_message": "INSERT INTO messages (thread, content, role) VALUES (?, ?, ?)",
    "post_message_with_timestamp": "INSERT INTO messages (thread, content, role, timestamp) VALUES (?, ?, ?, ?)",
    "update_message": "UPDATE messages SET timestamp = ?, content = COALESCE(?, content) WHERE id = ?",
    "delete_messages_more_recent": "DELETE FROM messages WHERE id = ? OR (thread = (SELECT thread FROM messages WHERE id = ?) AND timestamp > (SELECT timestamp FROM messages WHERE id = ?))",
    "delete_scheduled_messages_from_thread": "DELETE FROM messages WHERE thread = ? AND timestamp > CURRENT_TIMESTAMP",
    # THREADS
    "post_thread": "INSERT INTO threads (user, chatbot) VALUES (?, ?) RETURNING id",
    "get_thread": "SELECT id, user, chatbot, phase FROM threads WHERE id = ?",
    "get_threads_by_user": "SELECT id, user, chatbot, phase FROM threads WHERE user = ?",
    "get_latest_thread": "SELECT MAX(id) FROM threads WHERE user = ? AND chatbot = ?",
    # EVENTS
    "post_event": "INSERT INTO events (chatbot, type, content) VALUES (?, ?, ?) RETURNING id",
    "get_events_by_type_and_chatbot": "SELECT id, timestamp, content FROM events WHERE type = ? AND chatbot = ?",
    "delete_event": "DELETE FROM events WHERE id = ?",
}


class Message(TypedDict):
    """
    Message type.
    """

    id: int
    content: str
    role: str
    timestamp: datetime
    user: str
    chatbot: str


class Thread(TypedDict):
    """
    Thread type.
    """

    id: int
    user: str
    chatbot: str
    phase: str


class Event(TypedDict):
    """
    Event type.
    """

    id: int
    timestamp: datetime
    content: str


class DB:
    """
    Class to manage the database.
    """

    def __init__(self, db_path: str = "database.db") -> None:
        self.db_path = db_path
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
            queries["post_thread"],
            (user, chatbot),
        )
        result = cursor.fetchone()[0]
        conn.commit()
        close()
        return result

    def get_thread(self, thread_id: int) -> Thread:
        """
        Get the user and chatbot for a thread.
        """
        _, cursor, close = self._setup()
        cursor.execute(
            queries["get_thread"],
            (thread_id,),
        )
        result = cursor.fetchone()
        close()
        if result:
            return Thread(
                id=result[0], user=result[1], chatbot=result[2], phase=result[3]
            )
        raise ValueError("Thread not found")

    def get_latest_thread(self, user: str, chatbot: str) -> int:
        """
        Get the latest thread for a user and chatbot.
        """
        _, cursor, close = self._setup()
        cursor.execute(
            queries["get_latest_thread"],
            (user, chatbot),
        )
        result = cursor.fetchone()
        close()
        if result[0]:
            return result[0]
        return 0

    def get_threads_by_user(self, user: str) -> List[Thread]:
        """
        Get all threads for a user.
        """
        _, cursor, close = self._setup()
        cursor.execute(
            queries["get_threads_by_user"],
            (user,),
        )
        result = cursor.fetchall()
        close()
        threads = []
        for thread in result:
            threads.append(
                Thread(
                    id=thread[0],
                    user=thread[1],
                    chatbot=thread[2],
                    phase=thread[3],
                )
            )
        return threads

    def post_message(
        self, thread: int, content: str, role: str, timestamp: datetime | None = None
    ) -> None:
        """
        Insert a message into the database.
        """
        conn, cursor, close = self._setup()
        if timestamp:
            cursor.execute(
                queries["post_message_with_timestamp"],
                (thread, content, role, convert_dt_ts(timestamp)),
            )
        else:
            cursor.execute(
                queries["post_message"],
                (thread, content, role),
            )
        conn.commit()
        close()

    def get_messages(self) -> List[Message]:
        """
        Get all messages from the database.
        """
        _, cursor, close = self._setup()
        cursor.execute(queries["get_messages"])
        result = cursor.fetchall()
        close()
        messages = []
        for message in result:
            messages.append(
                Message(
                    id=message[0],
                    content=message[1],
                    role=message[2],
                    timestamp=convert_ts_dt(message[3]),
                    user=message[4],
                    chatbot=message[5],
                )
            )
        return messages

    def get_messages_by_thread(self, thread_id: int) -> List[Message]:
        """
        Get all messages from the database.
        """
        _, cursor, close = self._setup()
        cursor.execute(queries["get_messages_by_thread"], (thread_id,))
        result = cursor.fetchall()
        close()
        messages = []
        for message in result:
            messages.append(
                Message(
                    id=message[0],
                    content=message[1],
                    role=message[2],
                    timestamp=convert_ts_dt(message[3]),
                    user=message[4],
                    chatbot=message[5],
                )
            )
        return messages

    def get_messages_by_character(self, chatbot: str) -> List[Message]:
        """
        Get all messages from the database.
        """
        _, cursor, close = self._setup()
        cursor.execute(queries["get_messages_by_character"], (chatbot,))
        result = cursor.fetchall()
        close()
        messages = []
        for message in result:
            messages.append(
                Message(
                    id=message[0],
                    content=message[1],
                    role=message[2],
                    timestamp=convert_ts_dt(message[3]),
                    user=message[4],
                    chatbot=message[5],
                )
            )
        return messages

    def delete_messages_more_recent(self, message_id: int) -> None:
        """
        Delete selected message and all more recent messages.
        """
        conn, cursor, close = self._setup()
        cursor.execute(
            queries["delete_messages_more_recent"],
            (message_id, message_id, message_id),
        )
        conn.commit()
        close()

    def delete_scheduled_messages_from_thread(self, thread_id: int) -> None:
        """
        Delete all scheduled messages from a thread.
        """
        conn, cursor, close = self._setup()
        cursor.execute(
            queries["delete_scheduled_messages_from_thread"],
            (thread_id,),
        )
        conn.commit()
        close()

    def get_scheduled_message(self, thread_id: int) -> int:
        """
        Checks the DB for any scheduled messages returning the message id.
        """
        _, cursor, close = self._setup()
        cursor.execute(
            queries["get_scheduled_message"],
            (thread_id,),
        )
        result = cursor.fetchone()
        close()
        return result[0] if result else 0

    def update_message(
        self, message_id: int, timestamp: datetime, content: str | None = None
    ) -> None:
        """
        Updates message timestamp and content
        """
        conn, cursor, close = self._setup()
        cursor.execute(
            queries["update_message"],
            (convert_dt_ts(timestamp), content, message_id),
        )
        conn.commit()
        close()

    def post_event(self, chatbot: str, event_type: str, content: str) -> int:
        """
        Insert an event into the database.
        """
        conn, cursor, close = self._setup()
        cursor.execute(
            queries["post_event"],
            (chatbot, event_type, content),
        )
        result = cursor.fetchone()[0]
        conn.commit()
        close()
        return result

    def get_events_by_type_and_chatbot(
        self, event_type: str, chatbot: str
    ) -> List[Event]:
        """
        Get all events from the database.
        """
        _, cursor, close = self._setup()
        cursor.execute(
            queries["get_events_by_type_and_chatbot"],
            (event_type, chatbot),
        )
        result = cursor.fetchall()
        close()
        events = []
        for event in result:
            events.append(
                Event(
                    id=event[0],
                    timestamp=convert_ts_dt(event[1]),
                    content=event[2],
                )
            )
        return events

    def delete_event(self, event_id: int) -> None:
        """
        Delete an event from the database.
        """
        conn, cursor, close = self._setup()
        cursor.execute(
            queries["delete_event"],
            (event_id,),
        )
        if cursor.rowcount != 1:
            close()
            raise ValueError("Event not found")
        conn.commit()
        close()


def convert_ts_dt(timestamp: str) -> datetime:
    """
    Convert a timestamp string to a datetime object.
    """
    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    return dt.replace(tzinfo=timezone.utc)


def convert_dt_ts(dt: datetime) -> str:
    """
    Convert a datetime object to a timestamp string.
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")
