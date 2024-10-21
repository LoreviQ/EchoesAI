-- schema.sql
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    thread INTEGER NOT NULL,
    content TEXT NOT NULL,
    role TEXT NOT NULL,
    FOREIGN KEY(thread) REFERENCES threads(id)
);

CREATE TABLE IF NOT EXISTS threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started TEXT DEFAULT CURRENT_TIMESTAMP,
    user TEXT NOT NULL,
    chatbot TEXT NOT NULL,
    phase INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    chatbot TEXT NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    chatbot TEXT NOT NULL,
    description TEXT,
    prompt TEXT,
    caption TEXT,
    image_path TEXT
);