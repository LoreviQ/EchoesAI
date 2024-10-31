"""
This file contains the tests for the database/main.py file.
"""

# pylint: disable=redefined-outer-name unused-argument

import pytest

import database as db


@pytest.fixture
def test_db() -> None:
    """Create the database."""
    db.create_db()


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
