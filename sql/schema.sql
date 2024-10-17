-- schema.sql
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    thread INTEGER,
    content TEXT,
    role TEXT,
    FOREIGN KEY(thread) REFERENCES threads(id)
);

CREATE TABLE IF NOT EXISTS threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started TEXT DEFAULT CURRENT_TIMESTAMP,
    user TEXT,
    chatbot TEXT
);