import sqlite3


class DB:
    def __init__(self) -> None:
        # Connect to the database
        self.conn = sqlite3.connect("database.db")
        self.cursor = self.conn.cursor()

        # Create the schema if it doesn't exist
        with open("./sql/schema.sql", "r", encoding="utf-8") as file:
            schema = file.read()
        self.cursor.executescript(schema)
        self.conn.commit()


if __name__ == "__main__":
    db = DB()
