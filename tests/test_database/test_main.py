"""
This file contains the tests for the database/main.py file.
"""

# pylint: disable=redefined-outer-name unused-argument

from typing import Generator

import pytest
from sqlalchemy import create_engine

import database as db


@pytest.fixture
def test_db(monkeypatch) -> None:
    """Create the database."""
    db.create_db()


@pytest.fixture
def test_db_2(monkeypatch) -> Generator[None, None, None]:
    """Create the database."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        echo=True,
    )
    monkeypatch.setattr("database.main.ENGINE", engine)
    db.create_db(engine)
    yield
    engine.dispose()


def test_create_db() -> None:
    """Test the create_db function."""

    db.create_db()
    assert True


def test_insert_character(test_db: None) -> None:
    """Test the insert_character function."""

    char = db.Character(
        name="test",
        path_name="test",
    )
    result = db.insert_character(char)
    assert result == 1
