"""Database operations for the messages table."""

from typing import Any, List

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.engine import Row

from .db_types import Message, QueryOptions, messages_table, threads_table
from .main import ENGINE


def _row_to_message(row: Row[Any]) -> Message:
    """Convert a row to a message."""
    return Message(
        id=row.id,
        timestamp=row.timestamp,
        thread_id=row.thread_id,
        content=row.content,
        role=row.role,
    )


def insert_message(values: Message) -> int:
    """Insert a message into the database."""
    stmt = insert(messages_table).values(values)
    with ENGINE.begin() as conn:
        result = conn.execute(stmt)
        return result.inserted_primary_key[0]


def select_message(message_id: int) -> Message:
    """Select a message from the database."""
    stmt = select(messages_table).where(messages_table.c.id == message_id)
    with ENGINE.connect() as conn:
        result = conn.execute(stmt)
        message = result.fetchone()
        if message is None:
            raise ValueError(f"no message found with id: {message_id}")
        return _row_to_message(message)


def select_messages(
    message_query: Message = Message(), options: QueryOptions = QueryOptions()
) -> List[Message]:
    """Select messages from the database."""
    conditions = []
    for key, value in message_query.items():
        conditions.append(getattr(messages_table.c, key) == value)
    stmt = select(messages_table).where(*conditions)
    if options.get("limit"):
        stmt = stmt.limit(options["limit"])
    if options.get("orderby"):
        if options.get("order") == "desc":
            stmt = stmt.order_by(getattr(messages_table.c, options["orderby"]).desc())
        else:
            stmt = stmt.order_by(getattr(messages_table.c, options["orderby"]).asc())
    with ENGINE.connect() as conn:
        result = conn.execute(stmt)
        return [_row_to_message(row) for row in result]


def select_scheduled_message(thread_id: int) -> Message:
    """Select the next scheduled message for a thread."""
    stmt = (
        select(messages_table)
        .where(messages_table.c.thread_id == thread_id)
        .where(messages_table.c.timestamp > func.now())  # pylint: disable=not-callable
        .order_by(messages_table.c.timestamp.asc())
        .limit(1)
    )
    with ENGINE.connect() as conn:
        result = conn.execute(stmt)
        message = result.fetchone()
        if message is None:
            raise ValueError("No scheduled messages found.")
        return _row_to_message(message)


def select_messages_by_character(char_id: int) -> List[Message]:
    """Select messages from the database by character."""
    stmt = (
        select(messages_table)
        .select_from(
            messages_table.join(
                threads_table, messages_table.c.thread_id == threads_table.c.id
            )
        )
        .where(threads_table.c.char_id == char_id)
    )
    with ENGINE.connect() as conn:
        result = conn.execute(stmt)
        return [_row_to_message(row) for row in result]


def delete_message(message_id: int) -> None:
    """Delete a message from the database."""
    stmt = delete(messages_table).where(messages_table.c.id == message_id)
    with ENGINE.begin() as conn:
        conn.execute(stmt)


def delete_messages_more_recent(message_id: int) -> None:
    """Deletes the given message and all messages more recent than it in the same thread."""
    subquery_thread_id = (
        select(messages_table.c.thread_id)
        .where(messages_table.c.id == message_id)
        .scalar_subquery()
    )
    subquery_timestamp = (
        select(messages_table.c.timestamp)
        .where(messages_table.c.id == message_id)
        .scalar_subquery()
    )

    stmt = delete(messages_table).where(
        (messages_table.c.id == message_id)
        | (
            (messages_table.c.thread_id == subquery_thread_id)
            & (messages_table.c.timestamp > subquery_timestamp)
        )
    )

    with ENGINE.begin() as conn:
        conn.execute(stmt)


def delete_scheduled_messages(thread_id: int) -> None:
    """Delete all scheduled messages for a thread."""
    stmt = delete(messages_table).where(
        (messages_table.c.thread_id == thread_id)
        & (messages_table.c.timestamp > func.now())  # pylint: disable=not-callable
    )
    with ENGINE.begin() as conn:
        conn.execute(stmt)


def update_message(message: Message) -> None:
    """Update a message in the database."""
    stmt = (
        update(messages_table)
        .where(messages_table.c.id == message["id"])
        .values(message)
    )
    with ENGINE.begin() as conn:
        conn.execute(stmt)
