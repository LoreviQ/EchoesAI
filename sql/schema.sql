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
    character INTEGER NOT NULL,
    phase INTEGER DEFAULT 0,
    FOREIGN KEY(character) REFERENCES characters(id)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    character INTEGER NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY(character) REFERENCES characters(id)
);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    character INTEGER NOT NULL,
    description TEXT,
    prompt TEXT,
    caption TEXT,
    image_path TEXT,
    FOREIGN KEY(character) REFERENCES characters(id)
);

CREATE TABLE IF NOT EXISTS characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    age INTEGER,
    height TEXT,
    personality TEXT,
    appearance TEXT,
    loves TEXT,
    hates TEXT,
    details TEXT,
    scenario TEXT,
    important TEXT,
    initial_message TEXT,
    favorite_colour TEXT,
    phases boolean,
    img_gen boolean
);

CREATE TABLE IF NOT EXISTS phases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stage INTEGER NOT NULL,
    character INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    response_time TEXT,
    min_rt INTEGER,
    max_rt INTEGER,
    names TEXT,
    events TEXT,
    advance_conditions TEXT,
    FOREIGN KEY(character) REFERENCES characters(id)
);

CREATE TABLE IF NOT EXISTS img_gen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character INTEGER NOT NULL,
    model TEXT NOT NULL,
    global_positive TEXT,
    global_negative TEXT,
    additional_networks TEXT,
    FOREIGN KEY(character) REFERENCES characters(id)
);