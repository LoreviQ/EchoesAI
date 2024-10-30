"""Database operations for the threads table."""

from datetime import datetime, timezone
from typing import List

from .characters import select_character_by_id
from .main import (
    _placeholder_gen,
    connect_to_db,
    convert_dt_ts,
    general_insert_returning_id,
)
from .messages import insert_message
from .types import Message, QueryOptions, Thread


def insert_thread(user_id: int, char_id: int) -> int:
    """
    Insert a new thread into the database returning the thread id.
    If the character has an initial message, insert it as the first message.
    """
    ph = _placeholder_gen()
    query = f"""
        INSERT INTO threads (user_id, char_id) 
        VALUES ({next(ph)}, {next(ph)}) 
        RETURNING id
    """
    thread_id = general_insert_returning_id(query, (user_id, char_id))
    thread = select_thread(thread_id)
    character = select_character_by_id(char_id)
    now = convert_dt_ts(datetime.now(timezone.utc))
    if character["initial_message"]:
        message = Message(
            thread_id=thread["id"],
            content=character["initial_message"],
            role="assistant",
            timestamp=now,
        )
        insert_message(message)
    return thread_id


def select_thread(thread_id: int) -> Thread:
    """
    Select the user and chatbot for a thread.
    """
    ph = _placeholder_gen()
    query = f"""
        SELECT id, started, user_id, char_id, phase 
        FROM threads 
        WHERE id = {next(ph)}
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
            user_id=result[2],
            char_id=result[3],
            phase=result[4],
        )
    raise ValueError("Thread not found")


def select_threads(thread_query: Thread, options: QueryOptions) -> List[Thread]:
    """
    General query for threads.
    """
    ph = _placeholder_gen()
    query = """
        SELECT id, started, user_id, char_id, phase 
        FROM threads 
    """
    conditions = []
    parameters = []
    for key, value in thread_query.items():
        if value is not None:
            conditions.append(f"{key} = {next(ph)}")
            parameters.append(value)

    if conditions:
        query += " WHERE "
        query += " AND ".join(conditions)

    if options.get("orderby"):
        query += f" ORDER BY {options['orderby']}"
        if options.get("order"):
            query += f" {options['order']}"
    if options.get("limit"):
        query += f" LIMIT {options['limit']}"

    _, cursor, close = connect_to_db()
    cursor.execute(query, parameters)
    results = cursor.fetchall()
    close()
    events: List[Thread] = []
    for result in results:
        events.append(
            Thread(
                id=result[0],
                started=result[1],
                user_id=result[2],
                char_id=result[3],
                phase=result[4],
            )
        )
    return events


def select_latest_thread(user: int, character: int) -> int:
    """
    Select the latest thread for a user and character.
    """
    ph = _placeholder_gen()
    query = f"""
        SELECT MAX(id) FROM threads 
        WHERE user_id = {next(ph)} 
            AND char_id = {next(ph)}
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


def select_threads_by_user(user: int) -> List[Thread]:
    """
    Select all threads for a user.
    """
    ph = _placeholder_gen()
    query = f"""
        SELECT id, started, user_id, char_id, phase 
        FROM threads 
        WHERE user_id = {next(ph)}
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
                user_id=thread[2],
                char_id=thread[3],
                phase=thread[4],
            )
        )
    return threads


def select_latest_thread_by_user(user: int) -> Thread:
    """
    Select the latest thread for a user.
    """
    ph = _placeholder_gen()
    query = f"""
        SELECT t.id, t.started, t.user_id, t.char_id, t.phase
        FROM threads t
        JOIN (
            SELECT thread_id, MAX(timestamp) AS latest_message
            FROM messages
            GROUP BY thread_id
        ) m ON t.id = m.thread_id
        WHERE t.user_id = {next(ph)}
        ORDER BY m.latest_message DESC
        LIMIT 1;
    """
    _, cursor, close = connect_to_db()
    cursor.execute(
        query,
        (user,),
    )
    result = cursor.fetchone()
    close()
    if result:
        return Thread(
            id=result[0],
            started=result[1],
            user_id=result[2],
            char_id=result[3],
            phase=result[4],
        )
    raise ValueError("Thread not found")
