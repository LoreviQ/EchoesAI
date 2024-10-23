from typing import List

from .main import connect_to_db, general_insert_returning_id
from .types import Character


def insert_character(character: Character) -> int:
    """
    Insert a character into the database.
    """
    # Check if name is provided
    if not character.get("name"):
        raise ValueError("The 'name' field is required.")
    # Remove 'id' from the character dictionary to allow auto-increment
    character_without_id = {
        key: value for key, value in character.items() if key != "id"
    }
    # Prepare the SQL statement and the values
    columns = ", ".join(character_without_id.keys())
    placeholders = ", ".join(["?"] * len(character_without_id))
    query = f"INSERT INTO characters ({columns}) VALUES ({placeholders}) RETURNING id"
    values = tuple(character_without_id.get(key) for key in character_without_id.keys())
    # Execute the query
    return general_insert_returning_id(query, values)


def select_character(character_id: int) -> Character:
    """
    Select a character from the database.
    """
    query = """
        SELECT 
            id, name, description, age, height, personality, appearance, loves, 
            hates, details, scenario, important, initial_message, 
            favorite_colour, phases, img_gen, 
            model, global_positive, global_negative
        FROM characters
        WHERE id = ?
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
            description=result[2],
            age=result[3],
            height=result[4],
            personality=result[5],
            appearance=result[6],
            loves=result[7],
            hates=result[8],
            details=result[9],
            scenario=result[10],
            important=result[11],
            initial_message=result[12],
            favorite_colour=result[13],
            phases=result[14],
            img_gen=result[15],
            model=result[16],
            global_positive=result[17],
            global_negative=result[18],
        )
    raise ValueError("Character not found")


def select_characters() -> List[Character]:
    """
    Select all characters from the database.
    """
    query = """
        SELECT id, name, description, age, height, personality, appearance, loves, hates, details, scenario, important, initial_message, favorite_colour, phases, img_gen
        FROM characters
    """
    _, cursor, close = connect_to_db()
    cursor.execute(query)
    result = cursor.fetchall()
    close()
    characters: List[Character] = []
    for character in result:
        characters.append(
            Character(
                id=character[0],
                name=character[1],
                description=character[2],
                age=character[3],
                height=character[4],
                personality=character[5],
                appearance=character[6],
                loves=character[7],
                hates=character[8],
                details=character[9],
                scenario=character[10],
                important=character[11],
                initial_message=character[12],
                favorite_colour=character[13],
                phases=character[14],
                img_gen=character[15],
            )
        )
    return characters
