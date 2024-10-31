"""
This file contains the tests for the database/main.py file.
"""

# pylint: disable=redefined-outer-name unused-argument

import pytest
from sqlalchemy import create_engine

from database.main import create_db


@pytest.fixture
def test_db(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patches the engine to a test db held only in memory."""
    test_string = "sqlite+pysqlite:///:memory:"
    test_engine = create_engine(test_string, echo=True)

    # Sevars for local database
    monkeypatch.setattr("database.main.engine", test_engine)
    monkeypatch.setattr("database.main.connector", None)
    monkeypatch.setattr("database.main.getconn", None)


def test_create_db(test_db: None) -> None:
    """Test the create_db function."""

    create_db()
    assert True
