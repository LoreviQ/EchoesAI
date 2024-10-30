"""Database operations for the users table."""

from .main import (
    _placeholder_gen,
    connect_to_db,
    general_commit_returning_none,
    general_insert_returning_id,
)
from .types import User


def insert_user(user: User) -> int:
    """
    Insert a user into the database.
    """
    ph = _placeholder_gen()
    query = f"""
        INSERT INTO users (username, password, email) 
        VALUES ({next(ph)}, {next(ph)}, {next(ph)}) 
        RETURNING id
    """
    return general_insert_returning_id(
        query,
        (
            user["username"],
            user["password"],
            user["email"],
        ),
    )


def select_user(username: str) -> User:
    """
    Select a user from the database.
    """
    ph = _placeholder_gen()
    query = f"""
        SELECT id, username, password, email
        FROM users
        WHERE username = {next(ph)}
    """
    _, cursor, close = connect_to_db()
    cursor.execute(
        query,
        (username,),
    )
    result = cursor.fetchone()
    close()
    if result:
        return User(
            id=result[0],
            username=result[1],
            password=result[2],
            email=result[3],
        )
    raise ValueError("User not found")


def update_user(user: User) -> None:
    """
    Update a user in the database.
    """
    ph = _placeholder_gen()
    query = f"""
        UPDATE users
        SET password = {next(ph)}, email = {next(ph)}
        WHERE username = {next(ph)}
    """
    general_commit_returning_none(
        query,
        (
            user["password"],
            user["email"],
            user["username"],
        ),
    )


def select_user_by_id(user_id: int) -> User:
    """
    Select a user from the database by id.
    """
    ph = _placeholder_gen()
    query = f"""
        SELECT id, username, password, email
        FROM users
        WHERE id = {next(ph)}
    """
    _, cursor, close = connect_to_db()
    cursor.execute(
        query,
        (user_id,),
    )
    result = cursor.fetchone()
    close()
    if result:
        return User(
            id=result[0],
            username=result[1],
            password=result[2],
            email=result[3],
        )
    raise ValueError("User not found")
