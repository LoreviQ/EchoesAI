"""Miscellaneous database functions."""

from datetime import datetime, timezone
from sqlite3 import Connection, Cursor, connect
from typing import Callable, Tuple

DB_PATH = "database.db"


def create_db() -> None:
    """
    Create the database.
    """
    conn, _, close = connect_to_db()
    with open("./sql/schema.sql", "r", encoding="utf-8") as file:
        schema = file.read()
    with conn:
        conn.executescript(schema)
        conn.commit()
    close()


def connect_to_db() -> Tuple[Connection, Cursor, Callable[[], None]]:
    """
    Connect to the database.
    Returning the connection, cursor, and close function.
    """
    conn = connect(DB_PATH)
    cursor = conn.cursor()

    def close() -> None:
        cursor.close()
        conn.close()

    return conn, cursor, close


def convert_ts_dt(timestamp: str | None) -> datetime:
    """
    Convert a timestamp string to a datetime object.
    """
    if not timestamp:
        raise ValueError("Timestamp is None.")
    # remove data below a second
    timestamp = timestamp.split(".")[0]
    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    return dt.replace(tzinfo=timezone.utc)


def convert_dt_ts(dt: datetime | None) -> str:
    """
    Convert a datetime object to a timestamp string.
    """
    if not dt:
        raise ValueError("Datetime is None.")
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def general_commit_returning_none(query: str, params: Tuple = ()) -> None:
    """
    Execute a query that commits to the database.
    """
    conn, cursor, close = connect_to_db()
    cursor.execute(query, params)
    conn.commit()
    close()


def general_insert_returning_id(query: str, params: Tuple = ()) -> int:
    """
    Execute a query that inserts into the database and returns the id.
    Query must contain returning (int) statement.
    """
    conn, cursor, close = connect_to_db()
    cursor.execute(query, params)
    result = cursor.fetchone()[0]
    conn.commit()
    close()
    return int(result)
