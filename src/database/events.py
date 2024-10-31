"""Database operations for the events table."""

from typing import Any, List

from sqlalchemy import insert, select
from sqlalchemy.engine import Row

from .db_types import Event, events_table
from .main import engine


def _row_to_event(row: Row[Any]) -> Event:
    """Convert a row to a event."""
    return Event(
        id=row.id,
        timestamp=row.timestamp,
        char_id=row.char_id,
        type=row.type,
        content=row.content,
    )


def insert_event(values: Event) -> int:
    """Insert a event into the database."""
    stmt = insert(events_table).values(values)
    with engine.begin() as conn:
        result = conn.execute(stmt)
        return result.inserted_primary_key[0]


def select_events(event_query: Event = Event()) -> List[Event]:
    """Select events from the database, optionally with a query."""
    conditions = []
    for key, value in event_query.items():
        conditions.append(getattr(events_table.c, key) == value)
    stmt = select(events_table).where(*conditions)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        return [_row_to_event(row) for row in result]


def select_most_recent_event(char_id: int) -> Event:
    """Select the most recent event for a character."""
    stmt = (
        select(events_table)
        .where(events_table.c.char_id == char_id)
        .order_by(events_table.c.timestamp.desc())
        .limit(1)
    )
    with engine.connect() as conn:
        result = conn.execute(stmt)
        return _row_to_event(result.fetchone())


def delete_event(event_id: int) -> None:
    """Delete an event from the database."""
    stmt = events_table.delete().where(events_table.c.id == event_id)
    with engine.begin() as conn:
        conn.execute(stmt)
