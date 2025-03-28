CREATE TABLE users (
    id INTEGER  PRIMARY KEY,
    username    TEXT    UNIQUE,
    password_hash   TEXT
);

CREATE TABLE threads (
    id  INTEGER PRIMARY KEY,
    title   TEXT,
    content TEXT,
    stock_market    TEXT,
    sector  TEXT,
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

