"""Database operations for the characters table."""

from sqlalchemy import insert

from .db_types import Character, character_table
from .main import engine


def insert_character(values: Character) -> int:
    """Insert a character into the database."""
    stmt = insert(character_table).values(values)
    with engine.begin() as conn:
        result = conn.execute(stmt)
        return result.inserted_primary_key[0]
