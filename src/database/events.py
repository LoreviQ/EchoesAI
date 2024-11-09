"""Database operations for the events table."""

from typing import Any, List

from sqlalchemy import insert, select
from sqlalchemy.engine import Row

from .db_types import Event, QueryOptions, events_table
from .main import ENGINE


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
    with ENGINE.begin() as conn:
        result = conn.execute(stmt)
        return result.inserted_primary_key[0]


def select_events(
    event_query: Event = Event(), options: QueryOptions = QueryOptions()
) -> List[Event]:
    """Select events from the database, optionally with a query."""
    conditions = []
    for key, value in event_query.items():
        conditions.append(getattr(events_table.c, key) == value)
    stmt = select(events_table).where(*conditions)
    if options.get("limit"):
        stmt = stmt.limit(options["limit"])
    if options.get("offset"):
        stmt = stmt.offset(options["offset"])
    if options.get("orderby"):
        if options.get("order") == "desc":
            stmt = stmt.order_by(getattr(events_table.c, options["orderby"]).desc())
        else:
            stmt = stmt.order_by(getattr(events_table.c, options["orderby"]).asc())
    with ENGINE.connect() as conn:
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
    with ENGINE.connect() as conn:
        result = conn.execute(stmt)
        event = result.fetchone()
        if event is None:
            raise ValueError(f"no event found for character: {char_id}")
        return _row_to_event(event)


def delete_event(event_id: int) -> None:
    """Delete an event from the database."""
    stmt = events_table.delete().where(events_table.c.id == event_id)
    with ENGINE.begin() as conn:
        conn.execute(stmt)
