"""Miscellaneous database functions."""

import os
from typing import Any

from google.cloud.sql.connector import Connector
from sqlalchemy import Engine, create_engine

from .db_types import metadata_obj

connector = Connector()
# Used for GCP SQL psql connection
INSTANCE_CONNECTION_NAME = "echoesai:europe-west2:echoesai-db"
DB_NAME = "echoesai-new"
DB_USER = "echoes-db-manager"
DB_PASS = "fwRVZRtC5v&%Rsba"
LOCAL_DB = os.getenv("LOCAL_DB", "false").lower() == "true"
ENGINE: Engine


def getconn() -> Any:
    """
    Connect to the PostgreSQL database.
    Returning the connection.
    """
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pg8000",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME,
    )
    return conn


if LOCAL_DB:
    ENGINE = create_engine(
        "sqlite+pysqlite:///:memory:",
        echo=True,
    )
else:
    ENGINE = create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )


def create_db(engine: Engine | None = None) -> None:
    """Create the database."""
    if not engine:
        engine = ENGINE
    metadata_obj.create_all(ENGINE)
