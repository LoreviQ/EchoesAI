"""
This file contains the tests for the database/characters.py file.
"""

import os
from typing import Generator, Tuple

import pytest

# pylint: disable=redefined-outer-name unused-argument unused-import
import database as db


@pytest.fixture
def chars(
    monkeypatch,
) -> Generator[Tuple[db.Character, db.Character], None, None]:
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
    db.create_db()
    character_1 = db.Character(name="test character")
    character_2 = db.Character(name="test character 2")
    yield character_1, character_2
    os.remove(db_path)


def test_insert_character(chars) -> None:
    """
    Test the insert_character function.
    """
    character_id = db.insert_character(chars[0])
    assert character_id == 1
    character_id = db.insert_character(chars[1])
    assert character_id == 2


def test_select_character(chars) -> None:
    """
    Test the select_character function.
    """
    character_id = db.insert_character(chars[0])
    character = db.select_character(character_id)
    assert character["name"] == "test character"
    character_id = db.insert_character(chars[1])
    character = db.select_character(character_id)
    assert character["name"] == "test character 2"


def test_select_characters(chars) -> None:
    """
    Test the select_characters function.
    """
    db.insert_character(chars[0])
    db.insert_character(chars[1])
    characters = db.select_characters()
    assert len(characters) == 2
    assert characters[0]["name"] == "test character"
    assert characters[1]["name"] == "test character 2"
