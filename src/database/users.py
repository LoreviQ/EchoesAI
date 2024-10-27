"""Database operations for the users table."""

from .main import (
    connect_to_db,
    general_commit_returning_none,
    general_insert_returning_id,
)
from .types import User


def insert_user(user: User) -> int:
    """
    Insert a user into the database.
    """
    query = """
        INSERT INTO users (username, password, email) 
        VALUES (?, ?, ?) 
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
    query = """
        SELECT id, username, password, email
        FROM users
        WHERE username = ?
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
    query = """
        UPDATE users
        SET password = ?, email = ?
        WHERE username = ?
    """
    general_commit_returning_none(
        query,
        (
            user["password"],
            user["email"],
            user["username"],
        ),
    )
