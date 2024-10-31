"""Password utilities."""

import bcrypt

import database as db


def _hash_password(password: str) -> str:
    """Hash a password."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def insert_user(user: db.User) -> int:
    """
    Insert a user into the database with a hashed password.
    """
    assert user["password"]
    user["password"] = _hash_password(user["password"])
    return db.insert_user(user)


def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticate a user.
    Gets the hashed password from the database and compares it with bcrypt.
    """
    user = db.select_user(username)
    if user is None:
        return False
    assert user["password"]
    hashed = user["password"]
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
