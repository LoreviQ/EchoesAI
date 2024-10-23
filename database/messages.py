from typing import List, Tuple

from .main import (
    connect_to_db,
    convert_dt_ts,
    convert_ts_dt,
    general_commit_returning_none,
    general_insert_returning_id,
)
from .types import Message, Thread


def _general_select_returning_messages(query: str, params: Tuple = ()) -> List[Message]:
    _, cursor, close = connect_to_db()
    cursor.execute(query, params)
    result = cursor.fetchall()
    close()
    messages = []
    for message in result:
        messages.append(
            Message(
                id=message[0],
                timestamp=convert_ts_dt(message[3]),
                thread=Thread(
                    user=message[4],
                    character=message[5],
                ),
                content=message[1],
                role=message[2],
            )
        )
    return messages


def insert_message(message: Message) -> int:
    """
    Insert a message into the database.
    """
    assert message["thread"]
    assert message["thread"]["id"]
    assert message["content"]
    assert message["role"]
    if "timestamp" in message:
        query = """
            INSERT INTO messages (thread, content, role, timestamp) 
            VALUES (?, ?, ?, ?)
            returning id
        """
        return general_insert_returning_id(
            query,
            (
                message["thread"]["id"],
                message["content"],
                message["role"],
                convert_dt_ts(message["timestamp"]),
            ),
        )
    else:
        query = """
            INSERT INTO messages (thread, content, role) 
            VALUES (?, ?, ?)
            returning id
        """
        return general_insert_returning_id(
            query, (message["thread"]["id"], message["content"], message["role"])
        )


def select_message(message_id: int) -> Message:
    """
    Select a message from the database.
    """
    query = """
        SELECT m.id, m.content, m.role, m.timestamp, t.user, t.character 
        FROM messages as m JOIN threads as t ON m.thread = t.id 
        WHERE m.id = ?
    """
    _, cursor, close = connect_to_db()
    cursor.execute(
        query,
        (message_id,),
    )
    result = cursor.fetchone()
    close()
    if result:
        return Message(
            id=result[0],
            timestamp=convert_ts_dt(result[3]),
            thread=Thread(
                user=result[4],
                character=result[5],
            ),
            content=result[1],
            role=result[2],
        )
    raise ValueError("Message not found")


def select_messages_by_thread(thread_id: int) -> List[Message]:
    """
    Select messages from the database by thread.
    """
    query = """
        SELECT m.id, m.content, m.role, m.timestamp, t.user, t.character 
        FROM messages as m JOIN threads as t ON m.thread = t.id 
        WHERE thread = ?
    """
    return _general_select_returning_messages(query, (thread_id,))


def select_messages_by_character(character: int) -> List[Message]:
    """
    Select messages from the database by character.
    """
    query = """
        SELECT m.id, m.content, m.role, m.timestamp, t.user, t.character 
        FROM messages as m JOIN threads as t ON m.thread = t.id 
        WHERE t.character = ?
    """
    return _general_select_returning_messages(query, (character,))


def delete_messages_more_recent(message_id: int) -> None:
    """
    Delete selected message and all more recent messages.
    """
    query = """
        DELETE
        FROM messages 
        WHERE id = ? 
            OR (
                thread = (
                    SELECT thread 
                    FROM messages 
                    WHERE id = ?
                ) 
                AND timestamp > (
                    SELECT timestamp 
                    FROM messages 
                    WHERE id = ?
                )
            )
    """
    general_commit_returning_none(query, (message_id, message_id, message_id))


def delete_scheduled_messages_from_thread(thread_id: int) -> None:
    """
    Delete all scheduled messages from a thread.
    """
    query = """
        DELETE FROM messages 
        WHERE thread = ? 
            AND timestamp > CURRENT_TIMESTAMP
    """
    general_commit_returning_none(query, (thread_id,))


def select_scheduled_message_id(thread_id: int) -> int:
    """
    Checks the DB for any scheduled messages returning the message id.
    """
    query = """
        SELECT id FROM messages 
        WHERE thread = ? 
            AND timestamp > CURRENT_TIMESTAMP
    """
    _, cursor, close = connect_to_db()
    cursor.execute(
        query,
        (thread_id,),
    )
    result = cursor.fetchone()
    close()
    return result[0] if result else 0


def update_message(message: Message) -> None:
    """
    Update a message in the database.
    """
    query = """
        UPDATE messages 
        SET timestamp = ?, content = COALESCE(?, content) 
        WHERE id = ?
    """
    params = (
        convert_dt_ts(message["timestamp"]),
        message["content"],
        message["id"],
    )
    general_commit_returning_none(query, params)
