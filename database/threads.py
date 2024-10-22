from datetime import datetime
from typing import List, TypedDict

from .main import connect_to_db, general_insert_returning_id


class Thread(TypedDict):
    """
    Thread type.
    """

    id: int
    started: datetime
    user: str
    character: int
    phase: str


def insert_thread(user: str, character: int) -> int:
    """
    Insert a new thread into the database returning the thread id.
    """
    query = """
        INSERT INTO threads (user, character) 
        VALUES (?, ?) 
        RETURNING id
    """
    general_insert_returning_id(query, (user, character))


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


def select_latest_thread(user: str, chatbot: str) -> int:
    """
    Select the latest thread for a user and chatbot.
    """
    query = """
        SELECT MAX(id) FROM threads 
        WHERE user = ? 
            AND chatbot = ?
    """
    _, cursor, close = connect_to_db()
    cursor.execute(
        query,
        (user, chatbot),
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
