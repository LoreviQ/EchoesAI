"""Database operations for the events table."""

from typing import List

from .main import (
    _placeholder_gen,
    connect_to_db,
    general_commit_returning_none,
    general_insert_returning_id,
)
from .types import Event


def insert_event(event: Event) -> int:
    """
    Insert an event into the database.
    """
    ph = _placeholder_gen()
    query = f"""
        INSERT INTO events (character, type, content) 
        VALUES ({next(ph)}, {next(ph)}, {next(ph)}) 
        RETURNING id
    """
    return general_insert_returning_id(
        query,
        (
            event["character"],
            event["type"],
            event["content"],
        ),
    )


def select_events(event_query: Event = Event()) -> List[Event]:
    """
    Select events from the database based on a query.
    """
    ph = _placeholder_gen()
    query = """
        SELECT id, timestamp, character, type, content 
        FROM events 
    """
    conditions = []
    parameters = []
    for key, value in event_query.items():
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
    events: List[Event] = []
    for result in results:
        events.append(
            Event(
                id=result[0],
                timestamp=result[1],
                character=result[2],
                type=result[3],
                content=result[4],
            )
        )
    return events


def select_most_recent_event(character: int) -> Event:
    """
    Select the most recent event from the database.
    """
    ph = _placeholder_gen()
    query = f"""
        SELECT id, timestamp, type, content 
        FROM events 
        WHERE character = {next(ph)} 
        ORDER BY timestamp DESC LIMIT 1
    """

    _, cursor, close = connect_to_db()
    cursor.execute(
        query,
        (character,),
    )
    result = cursor.fetchone()
    close()
    if result:
        return Event(
            id=result[0],
            timestamp=result[1],
            character=character,
            type=result[2],
            content=result[3],
        )
    raise ValueError("Event not found")


def delete_event(event_id: int) -> None:
    """
    Delete an event from the database.
    """
    ph = _placeholder_gen()
    query = f"""
        DELETE FROM events 
        WHERE id = {next(ph)}
    """
    general_commit_returning_none(query, (event_id,))
