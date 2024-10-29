"""Database operations for the messages table."""

from typing import List, Tuple

from .main import (
    _placeholder_gen,
    connect_to_db,
    general_commit_returning_none,
    general_insert_returning_id,
)
from .types import Message, Thread


def _general_select_returning_messages(query: str, params: Tuple = ()) -> List[Message]:
    _, cursor, close = connect_to_db()
    cursor.execute(query, params)
    result = cursor.fetchall()
    close()
    messages: List[Message] = []
    for message in result:
        messages.append(
            Message(
                id=message[0],
                timestamp=message[3],
                thread_id=Thread(
                    id=message[4],
                    user_id=message[5],
                    char_id=message[6],
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
    ph = _placeholder_gen()
    assert message["thread_id"]
    assert message["thread_id"]["id"]
    assert message["content"]
    assert message["role"]
    if "timestamp" in message:
        query = f"""
            INSERT INTO messages (thread_id, content, role, timestamp) 
            VALUES ({next(ph)}, {next(ph)}, {next(ph)}, {next(ph)})
            returning id
        """
        return general_insert_returning_id(
            query,
            (
                message["thread_id"]["id"],
                message["content"],
                message["role"],
                message["timestamp"],
            ),
        )
    query = f"""
        INSERT INTO messages (thread_id, content, role) 
        VALUES ({next(ph)}, {next(ph)}, {next(ph)})
        returning id
    """
    return general_insert_returning_id(
        query, (message["thread_id"]["id"], message["content"], message["role"])
    )


def select_message(message_id: int) -> Message:
    """
    Select a message from the database.
    """
    ph = _placeholder_gen()
    query = f"""
        SELECT m.id, m.content, m.role, m.timestamp, t.id, t.user_id, t.char_id 
        FROM messages as m JOIN threads as t ON m.thread_id = t.id 
        WHERE m.id = {next(ph)}
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
            timestamp=result[3],
            thread_id=Thread(
                id=result[4],
                user_id=result[5],
                char_id=result[6],
            ),
            content=result[1],
            role=result[2],
        )
    raise ValueError("Message not found")


def select_messages(message_query: Message) -> List[Message]:
    """
    Select messages from the database by thread.
    """
    ph = _placeholder_gen()
    query = """
        SELECT m.id, m.content, m.role, m.timestamp, t.id, t.user_id, t.char_id 
        FROM messages as m JOIN threads as t ON m.thread_id = t.id 
    """
    conditions = []
    parameters = []
    for key, value in message_query.items():
        if value is not None:
            conditions.append(f"{key} = {next(ph)}")
            parameters.append(value)

    if conditions:
        query += " WHERE "
        query += " AND ".join(conditions)

    _, cursor, close = connect_to_db()
    cursor.execute(query, parameters)
    results = cursor.fetchall()
    close()

    messages: List[Message] = []
    for message in results:
        messages.append(
            Message(
                id=message[0],
                timestamp=message[3],
                thread=Thread(
                    id=message[4],
                    user=message[5],
                    character=message[6],
                ),
                content=message[1],
                role=message[2],
            )
        )
    return messages


def select_messages_by_thread(thread_id: int) -> List[Message]:
    """
    Select messages from the database by thread.
    """
    ph = _placeholder_gen()
    query = f"""
        SELECT m.id, m.content, m.role, m.timestamp, t.id, t.user_id, t.char_id 
        FROM messages as m JOIN threads as t ON m.thread_id = t.id 
        WHERE thread_id = {next(ph)}
    """
    return _general_select_returning_messages(query, (thread_id,))


def select_messages_by_character(character: int) -> List[Message]:
    """
    Select messages from the database by character.
    """
    ph = _placeholder_gen()
    query = f"""
        SELECT m.id, m.content, m.role, m.timestamp, t.id, t.user_id, t.char_id 
        FROM messages as m JOIN threads as t ON m.thread_id = t.id 
        WHERE t.char_id = {next(ph)}
    """
    return _general_select_returning_messages(query, (character,))


def delete_messages_more_recent(message_id: int) -> None:
    """
    Delete selected message and all more recent messages.
    """
    ph = _placeholder_gen()
    query = f"""
        DELETE
        FROM messages 
        WHERE id = {next(ph)} 
            OR (
                thread_id = (
                    SELECT thread_id 
                    FROM messages 
                    WHERE id = {next(ph)}
                ) 
                AND timestamp > (
                    SELECT timestamp 
                    FROM messages 
                    WHERE id = {next(ph)}
                )
            )
    """
    general_commit_returning_none(query, (message_id, message_id, message_id))


def delete_scheduled_messages_from_thread(thread_id: int) -> None:
    """
    Delete all scheduled messages from a thread.
    """
    ph = _placeholder_gen()
    query = f"""
        DELETE FROM messages 
        WHERE thread_id = {next(ph)} 
            AND timestamp > CURRENT_TIMESTAMP
    """
    general_commit_returning_none(query, (thread_id,))


def select_scheduled_message_id(thread_id: int) -> int:
    """
    Checks the DB for any scheduled messages returning the message id.
    """
    ph = _placeholder_gen()
    query = f"""
        SELECT id FROM messages 
        WHERE thread_id = {next(ph)} 
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
    ph = _placeholder_gen()
    query = f"""
        UPDATE messages 
        SET timestamp = {next(ph)}, content = COALESCE({next(ph)}, content) 
        WHERE id = {next(ph)}
    """
    params = (
        message["timestamp"],
        message.get("content", None),
        message["id"],
    )
    general_commit_returning_none(query, params)


def delete_message(message_id: int) -> None:
    """
    Delete a message from the database.
    """
    ph = _placeholder_gen()
    query = f"""
        DELETE FROM messages 
        WHERE id = {next(ph)}
    """
    general_commit_returning_none(query, (message_id,))
