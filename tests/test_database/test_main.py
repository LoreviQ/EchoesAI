"""
This file contains the tests for the database/main.py file.
"""

# pylint: disable=redefined-outer-name unused-argument
import os
from typing import Generator

import pytest

import database as db


@pytest.fixture
def db_path(monkeypatch) -> Generator[str, None, None]:
    """
    Create a DB object for testing and teardown after testing.
    """
    test_name = os.environ.get("PYTEST_CURRENT_TEST")
    if test_name is None:
        test_name = "unknown"
    else:
        test_name = test_name.split(":")[-1].split(" ")[0]
    db_path = f"test_database_{test_name}.db"
    monkeypatch.setattr("database.main.DB_PATH", db_path)
    db.main.create_db()
    yield db_path
    os.remove(db_path)


def test_create_db(db_path) -> None:
    """
    Test the create_db function.
    """
    db.main.create_db()
    assert os.path.exists(db_path)


def test_connect_to_db(db_path) -> None:
    """
    Test the connect_to_db function.
    """
    conn, cursor, close = db.main.connect_to_db()
    assert conn
    assert cursor
    assert close
    close()


def test_convert_ts_dt(db_path) -> None:
    """
    Test the convert_ts_dt function.
    """
    ts = "2021-07-01 12:00:00"
    dt = db.main.convert_ts_dt(ts)
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
    dt = db.main.convert_ts_dt("2021-07-01 12:00:00")
    ts = db.main.convert_dt_ts(dt)
    assert ts == "2021-07-01 12:00:00"


def test_general_commit_returning_none(db_path) -> None:
    """
    Test the general_commit_returning_none function.
    """

    query = "INSERT INTO characters (name) VALUES (?)"
    db.main.general_commit_returning_none(query, ("test_character",))
    _, cursor, close = db.main.connect_to_db()
    cursor.execute("SELECT name FROM characters")
    result = cursor.fetchone()
    assert result[0] == "test_character"
    close()


def test_general_insert_returning_id(db_path) -> None:
    """
    Test the general_insert_returning_id function.
    """
    query = "INSERT INTO characters (name) VALUES (?) RETURNING id"
    character_id = db.main.general_insert_returning_id(query, ("test_character",))
    assert character_id == 1
    _, cursor, close = db.main.connect_to_db()
    cursor.execute("SELECT name FROM characters")
    result = cursor.fetchone()
    assert result[0] == "test_character"
    close()
