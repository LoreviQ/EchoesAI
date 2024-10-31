"""Database operations for the threads table."""

from typing import Any, List

from sqlalchemy import insert, select
from sqlalchemy.engine import Row

from .db_types import QueryOptions, Thread, threads_table
from .main import engine


def _row_to_thread(row: Row[Any]) -> Thread:
    """Convert a row to a threads."""
    return Thread(
        id=row.id,
        started=row.started,
        user_id=row.user_id,
        char_id=row.char_id,
    )


def insert_thread(values: Thread) -> int:
    """Insert a thread into the database."""
    stmt = insert(threads_table).values(values)
    with engine.begin() as conn:
        result = conn.execute(stmt)
        return result.inserted_primary_key[0]


def select_thread(thread_id: int) -> Thread:
    """Select a thread from the database."""
    stmt = select(threads_table).where(threads_table.c.id == thread_id)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        thread = result.fetchone()
        if thread is None:
            raise ValueError(f"no thread found with id: {thread_id}")
        return _row_to_thread(thread)


def select_threads(
    thread_query: Thread = Thread(), options: QueryOptions = QueryOptions()
) -> List[Thread]:
    """Select threads from the database."""
    conditions = []
    for key, value in thread_query.items():
        conditions.append(getattr(threads_table.c, key) == value)
    stmt = select(threads_table).where(*conditions)
    if options.get("limit"):
        stmt = stmt.limit(options["limit"])
    if options.get("orderby"):
        if options.get("order") == "desc":
            stmt = stmt.order_by(getattr(threads_table.c, options["orderby"]).desc())
        else:
            stmt = stmt.order_by(getattr(threads_table.c, options["orderby"]).asc())
    with engine.connect() as conn:
        result = conn.execute(stmt)
        return [_row_to_thread(row) for row in result]


def select_latest_thread(user_id: int, char_id: int) -> Thread:
    """Select the latest thread from the database."""
    stmt = (
        select(threads_table)
        .where(threads_table.c.user_id == user_id)
        .where(threads_table.c.char_id == char_id)
        .order_by(threads_table.c.started.desc())
        .limit(1)
    )
    with engine.connect() as conn:
        result = conn.execute(stmt)
        thread = result.fetchone()
        if thread is None:
            raise ValueError(f"no thread found for user: {user_id} and char: {char_id}")
        return _row_to_thread(thread)
