from datetime import datetime
from typing import List, TypedDict

from .main import (
    connect_to_db,
    convert_ts_dt,
    general_commit_returning_none,
    general_insert_returning_id,
)


class Event(TypedDict):
    """
    Event type.
    """

    id: int
    timestamp: datetime
    character: int
    type: str
    content: str


def insert_event(event: Event) -> int:
    """
    Insert an event into the database.
    """
    query = """
        INSERT INTO events (character, type, content) 
        VALUES (?, ?, ?) 
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


def select_events_by_character(character: int) -> List[Event]:
    """
    Select events by character from the database.
    """
    query = """
        SELECT id, timestamp, type, content 
        FROM events 
        WHERE character = ?
    """
    _, cursor, close = connect_to_db()
    cursor.execute(
        query,
        (character,),
    )
    result = cursor.fetchall()
    close()
    events = []
    for event in result:
        events.append(
            Event(
                id=event[0],
                timestamp=convert_ts_dt(event[1]),
                character=character,
                type=event[2],
                content=event[3],
            )
        )
    return events


def select_most_recent_event(character: str) -> Event:
    """
    Select the most recent event from the database.
    """
    query = """
        SELECT id, timestamp, type, content 
        FROM events 
        WHERE character = ? 
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
            timestamp=convert_ts_dt(result[1]),
            character=character,
            type=result[2],
            content=result[3],
        )
    raise ValueError("Event not found")


def delete_event(event_id: int) -> None:
    """
    Delete an event from the database.
    """
    query = """
        DELETE FROM events 
        WHERE id = ?
    """
    general_commit_returning_none(query, (event_id,))
