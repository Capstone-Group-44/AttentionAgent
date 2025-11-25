PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE,
    display_name TEXT,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds FLOAT,
    screen_width INTEGER,
    screen_height INTEGER,

    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS focus_samples (
    focus_sample_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    left_iris_x FLOAT,
    left_iris_y FLOAT,
    right_iris_x FLOAT,
    right_iris_y FLOAT,

    face_x FLOAT,
    face_y FLOAT,
    face_z FLOAT,

    attention_state TEXT,
    focus_score FLOAT,

    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
);
