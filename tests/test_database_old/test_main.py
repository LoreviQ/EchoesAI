"""
This file contains the tests for the database/main.py file.
"""

# pylint: disable=redefined-outer-name unused-argument
import os
from sqlite3 import connect
from typing import Generator

import pytest

import database_old as db


@pytest.fixture
def db_init(
    monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest
) -> Generator[str, None, None]:
    """
    Initialises the db for testing returning the path to the db.
    """
    # Set the test database path
    test_name = os.environ.get("PYTEST_CURRENT_TEST")
    if test_name is None:
        test_name = "unknown"
    else:
        test_name = test_name.split(":")[-1].split(" ")[0]
    db_path = f"test_database_{test_name}.db"

    # Create the test database
    conn = connect(db_path)
    with open(
        "/home/lorevi/workspace/github.com/LoreviQ/EchoesAI/sql/schema.sql",
        "r",
        encoding="utf-8",
    ) as file:
        schema = file.read()
    with conn:
        conn.executescript(schema)
        conn.commit()
    conn.close()

    # Sevars for local database
    monkeypatch.setattr("database.main.DB_PATH", db_path)
    monkeypatch.setattr("database.main.LOCAL", True)

    # Cleanup the database after the test
    def cleanup() -> None:
        os.remove(db_path)

    request.addfinalizer(cleanup)

    # Return the path to the database
    yield db_path


def test_connect_to_db() -> None:
    """
    Test the connect_to_db function with GCP SQL.
    """
    conn, cursor, close = db.connect_to_db()
    assert conn
    assert cursor
    close()


def test_convert_ts_dt(db_init: str) -> None:
    """
    Test the convert_ts_dt function.
    """
    ts = "2021-07-01 12:00:00"
    dt = db.convert_ts_dt(ts)
    assert dt.year == 2021
    assert dt.month == 7
    assert dt.day == 1
    assert dt.hour == 12
    assert dt.minute == 0
    assert dt.second == 0


def test_convert_dt_ts() -> None:
    """
    Test the convert_dt_ts function.
    """
    dt = db.convert_ts_dt("2021-07-01 12:00:00")
    ts = db.convert_dt_ts(dt)
    assert ts == "2021-07-01 12:00:00"


def test_general_commit_returning_none(db_init: str) -> None:
    """
    Test the general_commit_returning_none function.
    """

    query = "INSERT INTO characters (name, path_name) VALUES (?, ?)"
    db.general_commit_returning_none(
        query,
        (
            "test_character",
            "test_character",
        ),
    )
    _, cursor, close = db.connect_to_db()
    cursor.execute("SELECT name FROM characters")
    result = cursor.fetchone()
    assert result[0] == "test_character"
    close()


def test_general_insert_returning_id(db_init: str) -> None:
    """
    Test the general_insert_returning_id function.
    """
    query = "INSERT INTO characters (name, path_name) VALUES (?, ?) RETURNING id"
    character_id = db.general_insert_returning_id(
        query,
        (
            "test_character",
            "test_character",
        ),
    )
    assert character_id == 1
    _, cursor, close = db.connect_to_db()
    cursor.execute("SELECT name FROM characters")
    result = cursor.fetchone()
    assert result[0] == "test_character"
    close()