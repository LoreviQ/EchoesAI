"""Database operations for the posts table."""

from typing import Any

from sqlalchemy import insert, select
from sqlalchemy.engine import Row

from .db_types import User, users_table
from .main import engine


def _row_to_user(row: Row[Any]) -> User:
    """Convert a row to a user."""
    return User(
        id=row.id,
        username=row.username,
        password=row.password,
        email=row.email,
    )


def insert_user(values: User) -> int:
    """Insert a user into the database."""
    stmt = insert(users_table).values(values)
    with engine.begin() as conn:
        result = conn.execute(stmt)
        return result.inserted_primary_key[0]


def select_user(username: str) -> User:
    """Select a user from the database."""
    stmt = select(users_table).where(users_table.c.username == username)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        user = result.fetchone()
        return _row_to_user(user)


def select_user_by_id(user_id: int) -> User:
    """Select a user from the database."""
    stmt = select(users_table).where(users_table.c.id == user_id)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        user = result.fetchone()
        return _row_to_user(user)


def update_user(user: User) -> None:
    """Update a user in the database."""
    stmt = (
        users_table.update()
        .where(users_table.c.id == user["id"])
        .values(
            username=user["username"],
            password=user["password"],
            email=user["email"],
        )
    )
    with engine.begin() as conn:
        conn.execute(stmt)
