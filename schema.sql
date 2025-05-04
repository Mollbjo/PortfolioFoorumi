CREATE TABLE users (
    id INTEGER  PRIMARY KEY,
    username    TEXT    UNIQUE,
    password_hash   TEXT
);

CREATE TABLE threads (
    id  INTEGER PRIMARY KEY,
    title   TEXT,
    content TEXT,
    parent_or_origin    TEXT,
    user_id INTEGER REFERENCES users
);

CREATE TABLE messages (
    id INTEGER  PRIMARY KEY,
    content TEXT,
    sent_at TEXT,
    user_id INTEGER REFERENCES users,
    thread_id   INTEGER REFERENCES threads
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);


CREATE TABLE thread_classes (
    id INTEGER  PRIMARY KEY,
    thread_id INTEGER REFERENCES threads,
    title TEXT,
    value TEXT
);

CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    thread_id INTEGER REFERENCES threads,
    image BLOB
);

CREATE TABLE votes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    thread_id INTEGER REFERENCES threads,
    vote INTEGER,
    UNIQUE(user_id, thread_id) 
);
