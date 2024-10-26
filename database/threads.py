from datetime import datetime, timezone
from typing import List

from .characters import select_character
from .main import connect_to_db, general_insert_returning_id
from .messages import insert_message
from .types import Message, Thread


def insert_thread(user_id: int, char_id: int) -> int:
    """
    Insert a new thread into the database returning the thread id.
    If the character has an initial message, insert it as the first message.
    """
    query = """
        INSERT INTO threads (user, character) 
        VALUES (?, ?) 
        RETURNING id
    """
    thread_id = general_insert_returning_id(query, (user_id, char_id))
    thread = select_thread(thread_id)
    character = select_character(char_id)
    if character["initial_message"]:
        message = Message(
            thread=thread,
            content=character["initial_message"],
            role="assistant",
            timestamp=datetime.now(timezone.utc),
        )
        insert_message(message)
    return thread_id


def select_thread(thread_id: int) -> Thread:
    """
    Select the user and chatbot for a thread.
    """
    query = """
        SELECT id, started, user, character, phase 
        FROM threads 
        WHERE id = ?
    """
    _, cursor, close = connect_to_db()
    cursor.execute(
        query,
        (thread_id,),
    )
    result = cursor.fetchone()
    close()
    if result:
        return Thread(
            id=result[0],
            started=result[1],
            user=result[2],
            character=result[3],
            phase=result[4],
        )
    raise ValueError("Thread not found")


def select_latest_thread(user: str, character: int) -> int:
    """
    Select the latest thread for a user and character.
    """
    query = """
        SELECT MAX(id) FROM threads 
        WHERE user = ? 
            AND character = ?
    """
    _, cursor, close = connect_to_db()
    cursor.execute(
        query,
        (user, character),
    )
    result = cursor.fetchone()
    close()
    if result[0]:
        return result[0]
    return 0


def select_threads_by_user(user: str) -> List[Thread]:
    """
    Select all threads for a user.
    """
    query = """
        SELECT id, started, user, character, phase 
        FROM threads 
        WHERE user = ?
    """
    _, cursor, close = connect_to_db()
    cursor.execute(
        query,
        (user,),
    )
    result = cursor.fetchall()
    close()
    threads = []
    for thread in result:
        threads.append(
            Thread(
                id=thread[0],
                started=thread[1],
                user=thread[2],
                character=thread[3],
                phase=thread[4],
            )
        )
    return threads
