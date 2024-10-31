"""Tests for the characters module in the database package."""

# pylint: disable=redefined-outer-name unused-argument unused-import

import database as db

from .test_main import test_db


def test_insert_character(test_db):
    """Test the insert_character function."""
    char = db.Character(
        name="test",
        path_name="test",
    )
    result = db.insert_character(char)
    assert result == 1


def test_select_character(test_db):
    """Test the select_character function."""
    char = db.Character(
        name="test",
        path_name="test",
    )
    db.insert_character(char)
    result = db.select_character("test")
    assert result["name"] == "test"
    assert result["path_name"] == "test"


def test_select_character_by_id(test_db):
    """Test the select_character_by_id function."""
    char = db.Character(
        name="test",
        path_name="test",
    )
    char_id = db.insert_character(char)
    result = db.select_character_by_id(char_id)
    assert result["name"] == "test"
    assert result["path_name"] == "test"


def test_select_characters_without_query(test_db):
    """Test the select_characters function without a query."""
    char = db.Character(
        name="test",
        path_name="test",
    )
    char2 = db.Character(
        name="test2",
        path_name="test2",
    )
    db.insert_character(char)
    db.insert_character(char2)
    result = db.select_characters()
    assert len(result) == 2
    assert result[0]["name"] == "test"
    assert result[0]["path_name"] == "test"
    assert result[1]["name"] == "test2"
    assert result[1]["path_name"] == "test2"


def test_select_characters_with_query(test_db):
    """Test the select_characters function with a query."""
    char = db.Character(
        name="test",
        path_name="test",
    )
    char2 = db.Character(
        name="test2",
        path_name="test2",
    )
    db.insert_character(char)
    db.insert_character(char2)
    result = db.select_characters(db.Character(name="test"))
    assert len(result) == 1
    assert result[0]["name"] == "test"
    assert result[0]["path_name"] == "test"


def test_select_characters_with_query_no_matching(test_db):
    """Test the select_characters function with a query that doesn't match any characters."""
    char = db.Character(
        name="test",
        path_name="test",
    )
    char2 = db.Character(
        name="test2",
        path_name="test2",
    )
    db.insert_character(char)
    db.insert_character(char2)
    result = db.select_characters(db.Character(name="not_a_character"))
    assert not result


def test_select_character_ids(test_db):
    """Test the select_character_ids function."""
    char = db.Character(
        name="test",
        path_name="test",
    )
    char2 = db.Character(
        name="test2",
        path_name="test2",
    )
    char_id = db.insert_character(char)
    char2_id = db.insert_character(char2)
    result = db.select_character_ids()
    assert len(result) == 2
    assert char_id in result
    assert char2_id in result
