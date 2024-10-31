"""Miscellaneous database functions."""

from google.cloud.sql.connector import Connector
from sqlalchemy import create_engine

from .db_types import metadata_obj

connector = Connector()
# Used for GCP SQL psql connection
INSTANCE_CONNECTION_NAME = "echoesai:europe-west2:echoesai-db"
DB_NAME = "echoesai-new"
DB_USER = "echoes-db-manager"
DB_PASS = "fwRVZRtC5v&%Rsba"


def getconn():
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


engine = create_engine(
    "postgresql+pg8000://",
    creator=getconn,
)


def create_db():
    """Create the database."""
    metadata_obj.create_all(engine)
