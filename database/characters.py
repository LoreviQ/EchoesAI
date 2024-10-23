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
            id, name, path_name, description, age, height, personality, 
            appearance, loves, hates, details, scenario, important, 
            initial_message, favorite_colour, phases, img_gen, 
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
        )
    raise ValueError("Character not found")


def select_character_by_path(path: str) -> Character:
    """
    Select a character from the database by path.
    """
    query = """
        SELECT 
            id, name, path_name, description, age, height, personality, 
            appearance, loves, hates, details, scenario, important, 
            initial_message, favorite_colour, phases, img_gen, 
            model, global_positive, global_negative
        FROM characters
        WHERE path_name = ?
    """
    _, cursor, close = connect_to_db()
    cursor.execute(
        query,
        (path,),
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
        )
    raise ValueError("Character not found")


def select_characters() -> List[Character]:
    """
    Select all characters from the database.
    """
    query = """
        SELECT id, name, path_name, description, age, height, personality, 
            appearance, loves, hates, details, scenario, important, 
            initial_message, favorite_colour, phases, img_gen, 
            model, global_positive, global_negative
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
                path_name=character[2],
                description=character[3],
                age=character[4],
                height=character[5],
                personality=character[6],
                appearance=character[7],
                loves=character[8],
                hates=character[9],
                details=character[10],
                scenario=character[11],
                important=character[12],
                initial_message=character[13],
                favorite_colour=character[14],
                phases=character[15],
                img_gen=character[16],
                model=character[17],
                global_positive=character[18],
                global_negative=character[19],
            )
        )
    return characters
