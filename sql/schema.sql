CREATE TABLE IF NOT EXISTS characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    path_name TEXT NOT NULL UNIQUE,
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
    phases boolean DEFAULT 0,
    img_gen boolean DEFAULT 0,
    model TEXT,
    global_positive TEXT,
    global_negative TEXT,
    profile_path TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started TEXT DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    char_id INTEGER NOT NULL,
    phase INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(char_id) REFERENCES characters(id)
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    thread_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    role TEXT NOT NULL,
    FOREIGN KEY(thread_id) REFERENCES threads(id)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    char_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY(char_id) REFERENCES characters(id)
);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    char_id INTEGER NOT NULL,
    description TEXT,
    image_post boolean DEFAULT 0,
    prompt TEXT,
    caption TEXT,
    image_path TEXT,
    FOREIGN KEY(char_id) REFERENCES characters(id)
);

CREATE TABLE IF NOT EXISTS phases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stage INTEGER NOT NULL,
    char_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    response_time TEXT,
    min_rt INTEGER,
    max_rt INTEGER,
    names TEXT,
    events TEXT,
    advance_conditions TEXT,
    FOREIGN KEY(char_id) REFERENCES characters(id)
);

