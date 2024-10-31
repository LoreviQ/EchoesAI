"""Database operations for the characters table."""

from typing import List

from .main import _placeholder_gen, connect_to_db, general_insert_returning_id
from .types import Character


def insert_character(character: Character) -> int:
    """
    Insert a character into the database.
    """
    # Check if name is provided
    if not character.get("name"):
        raise ValueError("The 'name' field is required.")
    # Remove 'id' from the character dictionary to allow auto-increment
    parsed_character = {
        key: value for key, value in character.items() if key != "id" and value
    }
    # Prepare the SQL statement and the values
    columns = ", ".join(parsed_character.keys())
    placeholders = ", ".join("%s" for _ in parsed_character.keys())
    query = f"INSERT INTO characters ({columns}) VALUES ({placeholders}) RETURNING id"
    values = tuple(parsed_character.get(key) for key in parsed_character.keys())
    # Execute the query
    return general_insert_returning_id(query, values)


def select_character(path_name: str) -> Character:
    """
    Select a character from the database.
    """
    ph = _placeholder_gen()
    query = f"""
        SELECT 
            id, name, path_name, description, age, height, personality, 
            appearance, loves, hates, details, scenario, important, 
            initial_message, favorite_colour, phases, img_gen, 
            model, global_positive, global_negative, profile_path
        FROM characters
        WHERE path_name = {next(ph)}
    """
    _, cursor, close = connect_to_db()
    cursor.execute(
        query,
        (path_name,),
    )
    result = cursor.fetchone()
    close()
    if result:
        return Character(
            id=result[0],
            name=result[1],
            path_name=result[2],
            description=result[3],
            age=result[4],
            height=result[5],
            personality=result[6],
            appearance=result[7],
            loves=result[8],
            hates=result[9],
            details=result[10],
            scenario=result[11],
            important=result[12],
            initial_message=result[13],
            favorite_colour=result[14],
            phases=result[15],
            img_gen=result[16],
            model=result[17],
            global_positive=result[18],
            global_negative=result[19],
            profile_path=result[20],
        )
    raise ValueError("character not found")


def select_character_by_id(character_id: int) -> Character:
    """
    Select a character from the database.
    """
    ph = _placeholder_gen()
    query = f"""
        SELECT 
            id, name, path_name, description, age, height, personality, 
            appearance, loves, hates, details, scenario, important, 
            initial_message, favorite_colour, phases, img_gen, 
            model, global_positive, global_negative, profile_path
        FROM characters
        WHERE id = {next(ph)}
    """
    _, cursor, close = connect_to_db()
    cursor.execute(
        query,
        (character_id,),
    )
    result = cursor.fetchone()
    close()
    if result:
        return Character(
            id=result[0],
            name=result[1],
            path_name=result[2],
            description=result[3],
            age=result[4],
            height=result[5],
            personality=result[6],
            appearance=result[7],
            loves=result[8],
            hates=result[9],
            details=result[10],
            scenario=result[11],
            important=result[12],
            initial_message=result[13],
            favorite_colour=result[14],
            phases=result[15],
            img_gen=result[16],
            model=result[17],
            global_positive=result[18],
            global_negative=result[19],
            profile_path=result[20],
        )
    raise ValueError("character not found")


def select_characters(
    character_query: Character = Character(),
) -> List[Character]:
    """Select characters from db that match the query."""
    ph = _placeholder_gen()
    query = """
        SELECT id, name, path_name, description, age, height, personality, 
            appearance, loves, hates, details, scenario, important, 
            initial_message, favorite_colour, phases, img_gen, 
            model, global_positive, global_negative, profile_path
        FROM characters
    """
    conditions = []
    parameters = []
    for key, value in character_query.items():
        if value is not None and key:
            conditions.append(f"{key} = {next(ph)}")
            parameters.append(value)

    if conditions:
        query += " WHERE "
        query += " AND ".join(conditions)

    _, cursor, close = connect_to_db()
    cursor.execute(query, parameters)
    results = cursor.fetchall()
    close()
    characters = []
    for result in results:
        characters.append(
            Character(
                id=result[0],
                name=result[1],
                path_name=result[2],
                description=result[3],
                age=result[4],
                height=result[5],
                personality=result[6],
                appearance=result[7],
                loves=result[8],
                hates=result[9],
                details=result[10],
                scenario=result[11],
                important=result[12],
                initial_message=result[13],
                favorite_colour=result[14],
                phases=result[15],
                img_gen=result[16],
                model=result[17],
                global_positive=result[18],
                global_negative=result[19],
                profile_path=result[20],
            )
        )
    return characters


def select_character_ids() -> List[int]:
    """Select all character ids from the database."""

    query = """
        SELECT id
        FROM characters
    """
    _, cursor, close = connect_to_db()
    cursor.execute(query)
    result = cursor.fetchall()
    close()
    return [character[0] for character in result]
