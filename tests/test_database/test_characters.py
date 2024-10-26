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
    char["id"] = db.insert_character(char)
    yield char


@pytest.fixture
def char_2() -> Generator[db.Character, None, None]:
    """
    Creates a character distinct from char_1 to be used in testing.
    """
    char = db.Character(name="test character 2", path_name="test_character_2")
    char["id"] = db.insert_character(char)
    yield char


def test_insert_character(db_init: str) -> None:
    """
    Test the insert_character function.
    """
    char_1 = db.Character(name="test character", path_name="test_character")
    char_2 = db.Character(name="test character 2", path_name="test_character_2")
    character_id = db.insert_character(char_1)
    assert character_id == 1
    character_id = db.insert_character(char_2)
    assert character_id == 2


def test_select_character(db_init: str) -> None:
    """
    Test the select_character function.
    """
    char_1 = db.Character(name="test character", path_name="test_character")
    char_2 = db.Character(name="test character 2", path_name="test_character_2")
    db.insert_character(char_1)
    db.insert_character(char_2)
    assert char_1["path_name"]
    assert char_2["path_name"]
    character_1 = db.select_character(char_1["path_name"])
    character_2 = db.select_character(char_2["path_name"])
    assert character_1["name"] == char_1["name"]
    assert character_2["name"] == char_2["name"]


def test_select_character_by_id(db_init: str) -> None:
    """
    Test the select_character_by_id function.
    """
    char_1 = db.Character(name="test character", path_name="test_character")
    char_2 = db.Character(name="test character 2", path_name="test_character_2")
    character_1_id = db.insert_character(char_1)
    character_2_id = db.insert_character(char_2)
    character_1 = db.select_character_by_id(character_1_id)
    character_2 = db.select_character_by_id(character_2_id)
    assert character_1["name"] == char_1["name"]
    assert character_2["name"] == char_2["name"]


def test_select_characters(db_init: str) -> None:
    """
    Test the select_characters function.
    """
    char_1 = db.Character(name="test character", path_name="test_character")
    char_2 = db.Character(name="test character 2", path_name="test_character_2")
    db.insert_character(char_1)
    db.insert_character(char_2)
    characters = db.select_characters()
    assert len(characters) == 2
    assert characters[0]["name"] == char_1["name"]
    assert characters[1]["name"] == char_2["name"]


def test_select_characters_by_query_path(db_init: str) -> None:
    """
    Test the select_characters function with a query specifying path.
    """
    char_1 = db.Character(name="test character", path_name="test_character")
    char_2 = db.Character(name="test character 2", path_name="test_character_2")
    character_1_id = db.insert_character(char_1)
    character_2_id = db.insert_character(char_2)
    character_1_query = db.Character(path_name=char_1["path_name"])
    character_2_query = db.Character(path_name=char_2["path_name"])
    character_1 = db.select_characters(character_1_query)[0]
    character_2 = db.select_characters(character_2_query)[0]
    assert character_1["id"] == character_1_id
    assert character_1["name"] == char_1["name"]
    assert character_2["id"] == character_2_id
    assert character_2["name"] == char_2["name"]


def test_select_characters_by_query_multiple(db_init: str) -> None:
    """
    Test the select_characters function with a query that returns multiple characters.
    """
    char_1 = db.Character(
        name="test character", path_name="test_character", img_gen=True
    )
    char_2 = db.Character(
        name="test character 2", path_name="test_character_2", img_gen=True
    )
    character_1_id = db.insert_character(char_1)
    character_2_id = db.insert_character(char_2)
    character_query = db.Character(img_gen=True)
    characters = db.select_characters(character_query)
    assert characters[0]["id"] == character_1_id
    assert characters[0]["name"] == char_1["name"]
    assert characters[1]["id"] == character_2_id
    assert characters[1]["name"] == char_2["name"]


def test_select_characters_by_query_none(db_init: str) -> None:
    """
    Test the select_characters function with a query that returns no characters.
    """
    char_1 = db.Character(
        name="test character", path_name="test_character", img_gen=True
    )
    char_2 = db.Character(
        name="test character 2", path_name="test_character_2", img_gen=True
    )
    db.insert_character(char_1)
    db.insert_character(char_2)
    character_query = db.Character(img_gen=False)
    characters = db.select_characters(character_query)
    assert len(characters) == 0
