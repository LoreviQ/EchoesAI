"""Database operations for the characters table."""

from typing import Any, List

from sqlalchemy import insert, select
from sqlalchemy.engine import Row

from .db_types import Character, characters_table
from .main import engine


def _row_to_character(row: Row[Any]) -> Character:
    """Convert a row to a character."""
    return Character(
        id=row.id,
        name=row.name,
        path_name=row.path_name,
        description=row.description,
        age=row.age,
        height=row.height,
        personality=row.personality,
        appearance=row.appearance,
        loves=row.loves,
        hates=row.hates,
        details=row.details,
        scenario=row.scenario,
        important=row.important,
        initial_message=row.initial_message,
        favorite_colour=row.favorite_colour,
        phases=row.phases,
        img_gen=row.img_gen,
        model=row.model,
        global_positive=row.global_positive,
        global_negative=row.global_negative,
        profile_path=row.profile_path,
    )


def insert_character(values: Character) -> int:
    """Insert a character into the database."""
    stmt = insert(characters_table).values(values)
    with engine.begin() as conn:
        result = conn.execute(stmt)
        return result.inserted_primary_key[0]


def select_character(path_name: str) -> Character:
    """Select a character from the database."""
    stmt = select(characters_table).where(characters_table.c.path_name == path_name)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        character = result.fetchone()
        if character is None:
            raise ValueError(f"no character found with path_name: {path_name}")
        return _row_to_character(character)


def select_character_by_id(character_id: int) -> Character:
    """Select a character from the database."""
    stmt = select(characters_table).where(characters_table.c.id == character_id)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        character = result.fetchone()
        if character is None:
            raise ValueError(f"no character found with id: {character_id}")
        return _row_to_character(character)


def select_characters(character_query: Character = Character()) -> List[Character]:
    """Select characters from the database, optionally with a query."""
    conditions = []
    for key, value in character_query.items():
        conditions.append(getattr(characters_table.c, key) == value)
    stmt = select(characters_table).where(*conditions)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        return [_row_to_character(row) for row in result]


def select_character_ids() -> List[int]:
    """Select all character ids from the database."""
    stmt = select(characters_table.c.id)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        return [row.id for row in result]
