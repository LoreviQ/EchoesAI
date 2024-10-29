"""Miscellaneous database functions."""

import sqlite3
from datetime import datetime, timezone
from typing import Any, Callable, Tuple

from google.cloud.sql.connector import Connector

connector = Connector()

LOCAL = False

# Used for local SQLite connection
DB_PATH = "database.db"

# Used for GCP SQL psql connection
INSTANCE_CONNECTION_NAME = "echoesai:europe-west2:echoesai-db"
DB_NAME = "echoesai-main"
DB_USER = "echoes-db-manager"
DB_PASS = "fwRVZRtC5v&%Rsba"


def connect_to_db() -> Tuple[Any, Any, Callable[[], None]]:
    """
    Connect to the PostgreSQL database.
    Returning the connection, cursor, and close function.
    """
    if LOCAL:
        # Connect to the local SQLite database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
    else:
        # Connect to the GCP SQL database
        conn = connector.connect(
            INSTANCE_CONNECTION_NAME,
            "pg8000",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME,
        )
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
