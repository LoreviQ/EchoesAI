"""
This file contains the tests for the database/characters.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

from typing import Generator

import pytest

import database as db
from tests.test_database.test_main import db_init


@pytest.fixture
def char_1() -> Generator[db.Character, None, None]:
    """
    Creates a character to be used in testing.
    """
    char = db.Character(name="test character", path_name="test_character")
    yield char


@pytest.fixture
def char_2() -> Generator[db.Character, None, None]:
    """
    Creates a character distict from char_1 to be used in testing.
    """
    char = db.Character(name="test character 2", path_name="test_character_2")
    yield char


@pytest.fixture
def char_1_ins(char_1) -> Generator[db.Character, None, None]:
    """
    Inserts char_1 into the database and yields it.
    """
    char_1["id"] = db.insert_character(char_1)
    yield char_1


@pytest.fixture
def char_2_ins(char_2) -> Generator[db.Character, None, None]:
    """
    Inserts char_2 into the database and yields it.
    """
    char_2["id"] = db.insert_character(char_2)
    yield char_2


def test_insert_character(
    db_init: str, char_1: db.Character, char_2: db.Character
) -> None:
    """
    Test the insert_character function.
    """
    character_id = db.insert_character(char_1)
    assert character_id == 1
    character_id = db.insert_character(char_2)
    assert character_id == 2


def test_select_character(
    db_init: str, char_1: db.Character, char_2: db.Character
) -> None:
    """
    Test the select_character function.
    """
    character_id = db.insert_character(char_1)
    character = db.select_character(character_id)
    assert character["name"] == char_1["name"]
    character_id = db.insert_character(char_2)
    character = db.select_character(character_id)
    assert character["name"] == char_2["name"]


def test_select_character_by_path(
    db_init: str, char_1: db.Character, char_2: db.Character
) -> None:
    """
    Test the select_character function.
    """
    assert char_1["path_name"]
    assert char_2["path_name"]
    character_id = db.insert_character(char_1)
    character = db.select_character_by_path(char_1["path_name"])
    assert character["id"] == character_id
    assert character["name"] == char_1["name"]
    character_id = db.insert_character(char_2)
    character = db.select_character_by_path(char_2["path_name"])
    assert character["id"] == character_id
    assert character["name"] == char_2["name"]


def test_select_characters(
    db_init: str, char_1: db.Character, char_2: db.Character
) -> None:
    """
    Test the select_characters function.
    """
    db.insert_character(char_1)
    db.insert_character(char_2)
    characters = db.select_characters()
    assert len(characters) == 2
    assert characters[0]["name"] == char_1["name"]
    assert characters[1]["name"] == char_2["name"]
