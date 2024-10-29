CREATE TABLE IF NOT EXISTS characters (
    id SERIAL PRIMARY KEY,
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
    phases BOOLEAN DEFAULT FALSE,
    img_gen BOOLEAN DEFAULT FALSE,
    model TEXT,
    global_positive TEXT,
    global_negative TEXT,
    profile_path TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS threads (
    id SERIAL PRIMARY KEY,
    started TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    char_id INTEGER NOT NULL,
    phase INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(char_id) REFERENCES characters(id)
);

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    thread_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    role TEXT NOT NULL,
    FOREIGN KEY(thread_id) REFERENCES threads(id)
);

CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    char_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY(char_id) REFERENCES characters(id)
);

CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    char_id INTEGER NOT NULL,
    description TEXT,
    image_post BOOLEAN DEFAULT FALSE,
    prompt TEXT,
    caption TEXT,
    image_path TEXT,
    FOREIGN KEY(char_id) REFERENCES characters(id)
);

CREATE TABLE IF NOT EXISTS phases (
    id SERIAL PRIMARY KEY,
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